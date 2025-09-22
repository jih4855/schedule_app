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

// 간단하고 안전한 하이라이팅 함수
function highlightPython(code) {
    let html = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

    // 문자열 하이라이팅 (가장 안전한 방식)
    html = html.replace(/"[^"]*"/g, '<span class="tok-str">$&</span>');
    html = html.replace(/'[^']*'/g, '<span class="tok-str">$&</span>');

    // 주석 하이라이팅
    html = html.replace(/#[^\n]*/g, '<span class="tok-comm">$&</span>');

    // 기본 키워드만 하이라이팅 (안전한 방식)
    const keywords = ['def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'import', 'from', 'return', 'True', 'False', 'None'];
    keywords.forEach(kw => {
        html = html.replace(new RegExp('\\b' + kw + '\\b', 'g'), `<span class="tok-kw">${kw}</span>`);
    });

    // 숫자 하이라이팅
    html = html.replace(/\b\d+\.?\d*\b/g, '<span class="tok-num">$&</span>');

    return html;
}

function highlightJS(code) {
    let html = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    
    // 키워드
    ['function', 'var', 'let', 'const', 'if', 'else', 'for', 'while', 'return', 'true', 'false', 'null', 'undefined'].forEach(kw => {
        html = html.replace(new RegExp('\\b' + kw + '\\b', 'g'), `<span class="tok-kw">${kw}</span>`);
    });
    
    // 문자열
    html = html.replace(/"[^"]*"/g, '<span class="tok-str">$&</span>');
    html = html.replace(/'[^']*'/g, '<span class="tok-str">$&</span>');
    html = html.replace(/`[^`]*`/g, '<span class="tok-str">$&</span>');
    
    // 주석
    html = html.replace(/\/\/[^\n]*/g, '<span class="tok-comm">$&</span>');
    
    // 숫자
    html = html.replace(/\b\d+\.?\d*\b/g, '<span class="tok-num">$&</span>');
    
    return html;
}

function highlightJSON(code) {
    let html = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    
    // 키
    html = html.replace(/"[^"]*"(?=\s*:)/g, '<span class="tok-prop">$&</span>');
    
    // 값 문자열
    html = html.replace(/:\s*"[^"]*"/g, function(match) {
        return match.replace(/"[^"]*"/, '<span class="tok-str">$&</span>');
    });
    
    // 불린/null
    html = html.replace(/\b(true|false|null)\b/g, '<span class="tok-kw">$1</span>');
    
    // 숫자
    html = html.replace(/\b\d+\.?\d*\b/g, '<span class="tok-num">$&</span>');
    
    return html;
}

// 코드 블록 하이라이팅 적용
function applyHighlighting() {
    document.querySelectorAll('pre code').forEach(codeEl => {
        if (codeEl.dataset.highlighted) return;

        try {
            const lang = (codeEl.getAttribute('data-lang') || '').toLowerCase();
            const code = codeEl.textContent;

            let html;
            if (lang === 'javascript' || lang === 'js') {
                html = highlightJS(code);
            } else if (lang === 'json') {
                html = highlightJSON(code);
            } else {
                html = highlightPython(code);
            }

            codeEl.innerHTML = html;
            codeEl.dataset.highlighted = 'true';

            // code-vscode 클래스 추가 (중요!)
            const pre = codeEl.closest('pre');
            if (pre) {
                pre.classList.add('code-vscode');
            }
        } catch (error) {
            console.error('하이라이팅 오류:', error);
            // 오류 발생시 원본 텍스트 유지
        }
    });
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
    // 하이라이팅 완전히 비활성화 - 기본 텍스트만 표시
    // applyHighlighting();

    // 모든 code 요소에 기본 스타일만 적용
    document.querySelectorAll('pre code').forEach(codeEl => {
        codeEl.style.color = '#e0e0e0';
        codeEl.style.fontFamily = 'Consolas, Monaco, monospace';
        codeEl.style.fontSize = '13px';
        codeEl.style.lineHeight = '1.4';
    });

    // 모든 details 요소를 기본으로 접힌 상태로 설정
    document.querySelectorAll('.docs-section details').forEach(d => { d.open = false; });

    // 첫 번째 섹션을 기본적으로 활성화
    setTimeout(() => {
        const firstLink = document.querySelector('.sidebar a');
        if (firstLink) {
            document.querySelectorAll('.sidebar a').forEach(l => l.classList.remove('active'));
            firstLink.classList.add('active');
        }
    }, 100);
});
