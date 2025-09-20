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

// 하이라이팅 함수들
function highlightPython(code) {
    let html = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

    // 문자열을 임시로 대체
    const strings = [];
    html = html.replace(/"[^"]*"/g, (match) => {
        strings.push(match);
        return `__STRING_${strings.length - 1}__`;
    });
    html = html.replace(/'[^']*'/g, (match) => {
        strings.push(match);
        return `__STRING_${strings.length - 1}__`;
    });

    // 주석을 임시로 대체
    const comments = [];
    html = html.replace(/#[^\n]*/g, (match) => {
        comments.push(match);
        return `__COMMENT_${comments.length - 1}__`;
    });

    // 키워드 하이라이팅
    const keywords = ['def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'import', 'from', 'return', 'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is', 'as', 'with', 'pass', 'break', 'continue'];
    keywords.forEach(kw => {
        html = html.replace(new RegExp('\\b' + kw + '\\b', 'g'), `<span class="tok-kw">${kw}</span>`);
    });

    // 내장 함수 하이라이팅 (print, input, len, range 등)
    const builtins = ['print', 'input', 'len', 'range', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple', 'open', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'max', 'min', 'sum', 'abs', 'round', 'type', 'isinstance', 'hasattr', 'getattr', 'setattr'];
    builtins.forEach(fn => {
        html = html.replace(new RegExp('\\b' + fn + '(?=\\s*\\()', 'g'), `<span class="tok-builtin">${fn}</span>`);
    });

    // 숫자 하이라이팅
    html = html.replace(/\b\d+\.?\d*\b/g, '<span class="tok-num">$&</span>');

    // 함수/클래스 이름 (정의 시)
    html = html.replace(/(<span class="tok-kw">def<\/span>\s+)(\w+)/g, '$1<span class="tok-fn">$2</span>');
    html = html.replace(/(<span class="tok-kw">class<\/span>\s+)(\w+)/g, '$1<span class="tok-class">$2</span>');

    // 함수 호출 (괄호 앞의 단어들) - 내장함수가 아닌 것들
    html = html.replace(/(?<!<span[^>]*>)\b([a-zA-Z_]\w*)(?=\s*\()(?![^<]*<\/span>)/g, (match, p1) => {
        // 이미 하이라이팅된 키워드나 내장함수가 아닌 경우만
        if (!keywords.includes(p1) && !builtins.includes(p1)) {
            return `<span class="tok-fn">${p1}</span>`;
        }
        return match;
    });

    // 점 표기법 (메소드/속성)
    html = html.replace(/\.(\w+)(?=\s*\()/g, '.<span class="tok-fn">$1</span>'); // 메소드
    html = html.replace(/\.(\w+)(?!\s*\()/g, '.<span class="tok-prop">$1</span>'); // 속성

    // 변수 하이라이팅 (할당문의 좌변) - 안전한 방법
    html = html.replace(/^(\s*)([a-zA-Z_]\w*)(\s*=)/gm, '$1<span class="tok-var">$2</span>$3');

    // for 루프의 변수들
    html = html.replace(/(<span class="tok-kw">for<\/span>\s+)([a-zA-Z_]\w*)(\s+<span class="tok-kw">in<\/span>)/g, '$1<span class="tok-var">$2</span>$3');

    // 딕셔너리의 키들 (따옴표 없는 경우)
    html = html.replace(/"([^"]+)"(\s*:)/g, '<span class="tok-str">"$1"</span>$2');

    // 문자열 복원
    strings.forEach((str, i) => {
        html = html.replace(`__STRING_${i}__`, `<span class="tok-str">${str}</span>`);
    });

    // 주석 복원
    comments.forEach((comment, i) => {
        html = html.replace(`__COMMENT_${i}__`, `<span class="tok-comm">${comment}</span>`);
    });

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
    applyHighlighting();
    // 모든 details 요소를 기본으로 접힌 상태로 설정
    document.querySelectorAll('.docs-section details').forEach(d => { d.open = false; });
});
