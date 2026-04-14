// SVG icons (inline to avoid external dependency)
const ICONS = {
    email: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 4L12 13 2 4"/></svg>',
    github: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>',
    scholar: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M5.242 13.769L0 9.5 12 0l12 9.5-5.242 4.269C17.548 11.249 14.978 9.5 12 9.5c-2.977 0-5.548 1.748-6.758 4.269zM12 10a7 7 0 1 0 0 14 7 7 0 0 0 0-14z"/></svg>',
    orcid: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zM7.369 4.378c.525 0 .947.431.947.947s-.422.947-.947.947a.95.95 0 0 1-.947-.947c0-.525.422-.947.947-.947zm-.722 3.038h1.444v10.041H6.647V7.416zm3.562 0h3.9c3.712 0 5.344 2.653 5.344 5.025 0 2.578-2.016 5.025-5.325 5.025h-3.919V7.416zm1.444 1.303v7.444h2.297c3.272 0 4.05-2.484 4.05-3.722 0-1.578-.947-3.722-3.891-3.722h-2.456z"/></svg>',
    linkedin: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>',
    semantic: '<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="10"/></svg>'
};

async function loadProfile() {
    try {
        const res = await fetch('data/profile.json');
        const profile = await res.json();
        renderProfile(profile);
    } catch (e) {
        console.warn('Could not load profile.json:', e);
    }
}

function renderProfile(p) {
    // Bio text
    const bioText = document.getElementById('bio-text');
    if (bioText) bioText.innerHTML = p.bio;

    // Scholar link in publications section
    const scholarLink = document.getElementById('scholar-link');
    if (scholarLink && p.links.google_scholar) {
        scholarLink.href = p.links.google_scholar;
    }

    // Bio links
    const linksEl = document.getElementById('bio-links');
    if (!linksEl) return;

    const linkItems = [
        { href: `mailto:${p.email}`, icon: ICONS.email, label: 'Email' },
        { href: p.links.google_scholar, icon: ICONS.scholar, label: 'Google Scholar' },
        { href: p.links.orcid, icon: ICONS.orcid, label: 'ORCID' },
        { href: p.links.github, icon: ICONS.github, label: 'GitHub' },
        { href: p.links.linkedin, icon: ICONS.linkedin, label: 'LinkedIn' },
    ];

    linksEl.innerHTML = linkItems
        .filter(l => l.href)
        .map(l => `<a href="${l.href}" target="_blank" rel="noopener">${l.icon} ${l.label}</a>`)
        .join('');

    // Experience
    const expList = document.getElementById('experience-list');
    if (expList && p.experience) {
        expList.innerHTML = p.experience.map(e => `
            <div class="exp-entry">
                <div class="exp-header">
                    <span class="exp-title">${e.title}</span>
                    <span class="exp-period">${e.period}</span>
                </div>
                <div class="exp-org">${e.organization}</div>
                <div class="exp-desc">${e.description}</div>
            </div>
        `).join('');
    }

    // Education
    const eduList = document.getElementById('education-list');
    if (eduList && p.education) {
        eduList.innerHTML = p.education.map(e => `
            <div class="exp-entry">
                <div class="exp-header">
                    <span class="exp-title">${e.degree}</span>
                    <span class="exp-period">${e.period}</span>
                </div>
                <div class="exp-org">${e.institution}${e.gpa ? ` (GPA: ${e.gpa})` : ''}</div>
            </div>
        `).join('');
    }
}

async function loadPublications() {
    try {
        const res = await fetch('data/publications.json');
        const data = await res.json();
        renderPublications(data.papers);
    } catch (e) {
        console.warn('Could not load publications.json:', e);
    }
}

function formatAuthors(authors) {
    return authors.map(a => {
        if (a === 'Mingyu Jeon') {
            return `<span class="me">${a}</span>`;
        }
        return a;
    }).join(', ');
}

function renderPublications(papers) {
    const container = document.getElementById('papers-list');
    if (!container) return;

    // Sort: highlighted first, then by year desc
    papers.sort((a, b) => {
        if (a.highlight !== b.highlight) return b.highlight ? 1 : -1;
        return b.year - a.year;
    });

    container.innerHTML = papers.map(p => {
        const links = [];
        if (p.arxiv) links.push(`<a href="https://arxiv.org/abs/${p.arxiv}" target="_blank">arXiv</a>`);
        if (p.pdf) links.push(`<a href="${p.pdf}" target="_blank">PDF</a>`);
        if (p.code) links.push(`<a href="${p.code}" target="_blank">Code</a>`);
        if (p.project) links.push(`<a href="${p.project}" target="_blank">Project</a>`);
        if (p.doi && !p.arxiv) links.push(`<a href="https://doi.org/${p.doi}" target="_blank">DOI</a>`);

        const badges = (p.badges || []).map(b => {
            let cls = 'paper-badge';
            if (b.toLowerCase().includes('award')) cls += ' award';
            if (b.toLowerCase() === 'oral') cls += ' oral';
            return `<span class="${cls}">${b}</span>`;
        }).join('');

        return `
            <div class="paper-entry${p.highlight ? ' highlight' : ''}">
                <div class="paper-title">${p.title}</div>
                <div class="paper-authors">${formatAuthors(p.authors)}</div>
                <div class="paper-venue">${p.venue}, ${p.year}</div>
                ${badges ? `<div class="paper-badges">${badges}</div>` : ''}
                ${links.length ? `<div class="paper-links">${links.join(' / ')}</div>` : ''}
            </div>
        `;
    }).join('');
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    loadProfile();
    loadPublications();
});
