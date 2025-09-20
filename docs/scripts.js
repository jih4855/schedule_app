/**
 * AI Multi-Agent Toolkit Documentation JavaScript
 */

/**
 * 코드 복사 기능
 * @param {string} id - 복사할 코드 요소의 ID
 */
function copy_button(id) {
    const code = document.getElementById(id);
    const codeText = code.textContent;
    navigator.clipboard.writeText(codeText).then(() => {
        alert('Code copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
}

/**
 * 텍스트를 URL 슬러그로 변환
 * @param {string} text - 변환할 텍스트
 * @returns {string} 슬러그화된 문자열
 */
function slugify(text) {
    return String(text || '')
        .toLowerCase()
        .replace(/[^\w가-힣\s-]/g, '')
        .trim()
        .replace(/\s+/g, '-');
}

/**
 * 사이드바 자동 생성
 * H3 제목과 details 요소를 기반으로 네비게이션을 생성
 */
function buildSidebar() {
    const container = document.querySelector('.docs-section');
    if (!container) return;

    // H3와 details를 섹션 구조로 매핑 (H3 밑의 details를 자식으로)
    const blocks = Array.from(container.children);
    const sections = [];
    let current = null;

    for (const el of blocks) {
        if (el.tagName === 'H3') {
            const title = el.textContent.trim();
            if (!el.id) el.id = slugify(title);
            current = { h3: el, items: [] };
            sections.push(current);
        } else if (el.tagName === 'DETAILS' && current) {
            const summary = el.querySelector('summary');
            const text = summary ? summary.textContent.trim() : 'details';
            if (!el.id) el.id = slugify((current.h3.textContent || '') + '-' + text);
            current.items.push({ el, text });
        }
    }

    // 사이드바 DOM 생성
    const nav = document.getElementById('sidebar-nav');
    if (!nav) return;
    nav.innerHTML = '';

    for (const sec of sections) {
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = `#${sec.h3.id}`;
        a.textContent = sec.h3.textContent.trim();
        li.appendChild(a);

        if (sec.items.length) {
            const ul = document.createElement('ul');
            ul.className = 'sub';
            for (const item of sec.items) {
                const sli = document.createElement('li');
                const sa = document.createElement('a');
                sa.href = `#${item.el.id}`;
                sa.textContent = item.text;
                // 서브항목 클릭 시 details 열기
                sa.addEventListener('click', () => { item.el.open = true; }, false);
                sli.appendChild(sa);
                ul.appendChild(sli);
            }
            li.appendChild(ul);
        }

        nav.appendChild(li);
    }
}

/**
 * 스크롤 위치에 따른 활성 네비게이션 하이라이트 설정
 */
function setupActiveHighlight() {
    const links = Array.from(document.querySelectorAll('.sidebar a'));
    const map = new Map(links.map(a => [a.getAttribute('href'), a]));

    const targets = Array.from(document.querySelectorAll('.docs-section h3, .docs-section details'));
    const obs = new IntersectionObserver((entries) => {
        entries.forEach(e => {
            if (e.isIntersecting) {
                const id = '#' + e.target.id;
                links.forEach(l => l.classList.remove('active'));
                const link = map.get(id);
                if (link) link.classList.add('active');
            }
        });
    }, { rootMargin: '0px 0px -70% 0px', threshold: 0.1 });

    targets.forEach(t => t.id && obs.observe(t));
}

/**
 * 문서 로드 완료 시 초기화
 */
document.addEventListener('DOMContentLoaded', () => {
    buildSidebar();
    setupActiveHighlight();
    // 모든 details 요소를 기본으로 접힌 상태로 설정
    document.querySelectorAll('.docs-section details').forEach(d => { d.open = false; });
});