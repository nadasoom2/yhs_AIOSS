
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.parse
from typing import Any, Optional

import numpy as np
import requests
from bs4 import BeautifulSoup
from sklearn.metrics.pairwise import cosine_similarity

# ── 환경변수 (hybrid_query_agent.py와 공유) ───────────────────────────────
VEC_WEIGHT         = float(os.environ.get("VEC_WEIGHT", "0.62"))
KW_WEIGHT          = float(os.environ.get("KW_WEIGHT", "0.38"))
CRAWL_MAX_DEPTH    = int(os.environ.get("CRAWL_MAX_DEPTH", "3"))
CRAWL_MAX_PAGES    = int(os.environ.get("CRAWL_MAX_PAGES", "10"))
CRAWL_FETCH_TIMEOUT = int(os.environ.get("CRAWL_FETCH_TIMEOUT", "6"))
CRAWL_SLEEP_SEC    = float(os.environ.get("CRAWL_SLEEP_SEC", "0.15"))


class Crawler:
    """
    ALLOWED_SITES 내에서 Playwright(JS 렌더링) + LLM 가이드 방식으로
    질문과 관련 있는 페이지를 찾아 크롤링하는 클래스.
    """

    def __init__(
        self,
        http: requests.Session,
        embedder: Any,
        llm: Any,
        allowed_sites: list[str],
        driver: Any,  # Neo4j driver (_save_external_chunks 용)
    ) -> None:
        self.http          = http
        self.embedder      = embedder
        self.llm           = llm
        self.ALLOWED_SITES = allowed_sites
        self.driver        = driver

    # ── 내부 유틸 ─────────────────────────────────────────────────────────

    def _tokens(self, text: str) -> list[str]:
        return [t.lower() for t in re.findall(r"[가-힣A-Za-z0-9]{2,}", text)]

    def _kw_score(self, query: str, target: str | list[str]) -> float:
        q = set(self._tokens(query))
        if not q:
            return 0.0
        if isinstance(target, list):
            t = set(tok for k in target for tok in self._tokens(k))
        else:
            t = set(self._tokens(target))
        if not t:
            return 0.0
        return len(q & t) / max(1, len(q))

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
        if not text:
            return []
        sents = re.split(r"(?<=[.!?。])\s+", text)
        out: list[str] = []
        buf = ""
        for s in sents:
            if len(buf) + len(s) > chunk_size and buf:
                out.append(buf.strip())
                buf = buf[-overlap:] + " " + s
            else:
                buf += (" " if buf else "") + s
        if buf.strip():
            out.append(buf.strip())
        return out

    # ── 페이지 fetch ──────────────────────────────────────────────────────

    def fetch_page_links_and_text(self, url: str) -> tuple[str, list[tuple[str, str]]]:
        """
        Playwright로 JS 렌더링 완료 후 페이지를 읽어옴.
        반환: (본문텍스트, [(메뉴경로>링크텍스트, 링크URL), ...])
        Playwright 미설치 시 requests로 폴백.
        """
        html = ""
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=15000, wait_until="networkidle")
                html = page.content()
                browser.close()
        except ImportError:
            print("[WARN] Playwright 미설치 → requests 폴백. 'pip install playwright && playwright install chromium' 권장")
            try:
                r = self.http.get(url, timeout=CRAWL_FETCH_TIMEOUT)
                r.raise_for_status()
                html = r.text
            except Exception:
                return "", []
        except Exception as e:
            print(f"[WARN] Playwright 오류({e}) → requests 폴백")
            try:
                r = self.http.get(url, timeout=CRAWL_FETCH_TIMEOUT)
                r.raise_for_status()
                html = r.text
            except Exception:
                return "", []

        soup = BeautifulSoup(html, "html.parser")

        # ── 메뉴 구조 추출: 상위메뉴 > 하위메뉴 경로로 라벨 구성 ──────────
        links: list[tuple[str, str]] = []
        seen_hrefs: set[str] = set()

        menu_roots = soup.select("nav, #gnb, #lnb, #snb, .gnb, .lnb, .nav, .menu, ul.depth1, ul.depth2")
        if not menu_roots:
            menu_roots = [soup]

        for root in menu_roots:
            for top_li in root.select("li"):
                top_label = ""
                top_a = top_li.find("a", recursive=False)
                if top_a:
                    top_label = top_a.get_text(strip=True)[:30]

                for a in top_li.select("a[href]"):
                    href = a.get("href", "").strip()
                    if not href or href.startswith("#") or href.startswith("javascript"):
                        continue
                    full_url = urllib.parse.urljoin(url, href).split("#")[0]
                    if not any(full_url.startswith(site) for site in self.ALLOWED_SITES):
                        continue
                    if full_url in seen_hrefs:
                        continue
                    seen_hrefs.add(full_url)
                    sub_label = a.get_text(strip=True)[:40]
                    if top_label and sub_label and top_label != sub_label:
                        label = f"{top_label} > {sub_label}"
                    else:
                        label = sub_label or top_label or full_url
                    links.append((label, full_url))

        # 메뉴에서 못 찾은 링크도 추가 수집
        for a in soup.select("a[href]"):
            href = a.get("href", "").strip()
            if not href or href.startswith("#") or href.startswith("javascript"):
                continue
            full_url = urllib.parse.urljoin(url, href).split("#")[0]
            if not any(full_url.startswith(site) for site in self.ALLOWED_SITES):
                continue
            if full_url in seen_hrefs:
                continue
            seen_hrefs.add(full_url)
            label = a.get_text(strip=True)[:60] or full_url
            links.append((label, full_url))

        # 본문 텍스트 추출
        for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
            tag.decompose()
        txt = re.sub(r"\s+", " ", soup.get_text(" ")).strip()
        return txt[:6000], links

    def fetch_page_text(self, url: str) -> str:
        text, _ = self.fetch_page_links_and_text(url)
        return text

    # ── LLM 링크 선택 ─────────────────────────────────────────────────────

    def llm_select_links(
        self,
        query: str,
        links: list[tuple[str, str]],
        visited: set[str],
    ) -> list[str]:
        """
        LLM이 메뉴 경로가 포함된 링크 목록을 보고 질문과 관련 있는 링크만 선택.
        이미 방문한 URL은 제외.
        """
        links = [(label, url) for label, url in links if url not in visited]
        if not links:
            return []
        if self.llm is None:
            return [url for _, url in links[:5]]

        lines = [f"{i+1}. {label} → {url}" for i, (label, url) in enumerate(links[:40])]
        prompt = (
            "다음은 대학교 홈페이지의 메뉴 구조입니다. (형식: 상위메뉴 > 하위메뉴 → URL)\n"
            "아래 질문에 답하기 위해 들어가봐야 할 메뉴의 번호만 골라 콤마로 나열하세요.\n"
            "최대 3개만 선택하고, 설명 없이 번호만 반환하세요.\n"
            "예시 출력: 2,5\n\n"
            f"질문: {query}\n\n"
            "메뉴 목록:\n" + "\n".join(lines)
        )
        try:
            resp = self.llm.generate_content(prompt, generation_config={"temperature": 0.0})
            text = (resp.text or "").strip()
            picked_nums = [x.strip() for x in re.split(r"[,\n]", text) if x.strip().isdigit()]
            selected_urls = []
            for num in picked_nums:
                idx = int(num) - 1
                if 0 <= idx < len(links):
                    selected_urls.append(links[idx][1])
            print(
                f"[CRAWL] LLM 선택 메뉴: "
                f"{[links[int(n)-1][0] for n in picked_nums if n.isdigit() and 0 <= int(n)-1 < len(links)]}",
                flush=True,
            )
            return selected_urls
        except Exception:
            return [url for _, url in links[:3]]

    # ── 메인 크롤링 ───────────────────────────────────────────────────────

    def crawl_fallback_chunks(self, query: str) -> list[tuple[str, str]]:
        """
        Playwright로 JS 렌더링 후 메뉴 구조를 파악,
        LLM이 질문과 관련 있는 메뉴를 선택해 타고 들어가는 방식으로 크롤링.
        ALLOWED_SITES 각각의 메인 페이지에서 시작.
        """
        all_chunks: list[tuple[str, str]] = []
        visited: set[str] = set()
        total_pages = 0

        for base_url in self.ALLOWED_SITES:
            if total_pages >= CRAWL_MAX_PAGES:
                break

            queue: list[tuple[str, int]] = [(base_url, 0)]

            while queue and total_pages < CRAWL_MAX_PAGES:
                current_url, depth = queue.pop(0)

                if current_url in visited:
                    continue
                visited.add(current_url)
                total_pages += 1

                print(f"[CRAWL] depth={depth} 방문: {current_url}", flush=True)
                page_text, links = self.fetch_page_links_and_text(current_url)
                time.sleep(CRAWL_SLEEP_SEC)

                if page_text:
                    for chunk in self._chunk_text(page_text):
                        all_chunks.append((current_url, chunk))

                if depth >= CRAWL_MAX_DEPTH:
                    continue

                if links:
                    selected_urls = self.llm_select_links(query, links, visited)
                    for next_url in selected_urls:
                        if next_url not in visited:
                            queue.append((next_url, depth + 1))

        return all_chunks

    # ── 스코어링 / 저장 ───────────────────────────────────────────────────

    def score_external_chunks(
        self,
        query: str,
        query_emb: np.ndarray,
        url_chunks: list[tuple[str, str]],
    ) -> list[tuple[str, str, float]]:
        if not url_chunks:
            return []
        embs = self.embedder.encode([c for _, c in url_chunks], show_progress_bar=False)
        out: list[tuple[str, str, float]] = []
        for (u, c), e in zip(url_chunks, embs):
            vec = float(cosine_similarity([query_emb], [e])[0][0])
            kw  = self._kw_score(query, c)
            score = VEC_WEIGHT * vec + KW_WEIGHT * kw
            out.append((u, c, score))
        out.sort(key=lambda x: x[2], reverse=True)
        return out

    def save_external_chunks(self, url_chunks: list[tuple[str, str]]) -> None:
        """크롤링 결과를 Neo4j ExternalChunk 노드로 저장"""
        if not url_chunks:
            return
        emb = self.embedder.encode([c for _, c in url_chunks], show_progress_bar=False)
        with self.driver.session() as s:
            for (u, text), e in zip(url_chunks, emb):
                cid = hashlib.sha1((u + "|" + text[:120]).encode("utf-8")).hexdigest()[:20]
                s.run(
                    """
                    MERGE (src:ExternalSource {url: $url})
                    MERGE (ch:ExternalChunk {chunk_id: $cid})
                    SET ch.text = $text,
                        ch.embedding_json = $emb,
                        ch.fetched_at = datetime()
                    MERGE (src)-[:HAS_CHUNK]->(ch)
                    """,
                    url=u,
                    cid=cid,
                    text=text,
                    emb=json.dumps(np.asarray(e, dtype=np.float32).tolist()),
                )