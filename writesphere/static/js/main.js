/* =============================================
   WriteSphere — Main JavaScript
   Pure Vanilla JS, No Dependencies
   ============================================= */

'use strict';

/* ── Utility ── */
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

function showToast(msg, type = 'success', duration = 3000) {
  $$('.toast').forEach(t => t.remove());
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => { t.style.opacity = '0'; t.style.transition = 'opacity .3s'; setTimeout(() => t.remove(), 300); }, duration);
}

function formatNumber(n) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
  if (n >= 1000) return (n / 1000).toFixed(1) + 'k';
  return n;
}

/* ============================================
   NAVBAR
   ============================================ */
(function initNavbar() {
  const navbar = $('#navbar');
  const hamburger = $('#hamburger');
  const mobileMenu = $('#mobileMenu');
  if (!navbar) return;

  // Scroll shadow
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 24);
  }, { passive: true });

  // Mobile menu toggle
  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', () => {
      const open = mobileMenu.classList.toggle('open');
      const spans = $$('span', hamburger);
      if (open) {
        spans[0].style.cssText = 'transform:rotate(45deg) translate(5px,5px)';
        spans[1].style.opacity = '0';
        spans[2].style.cssText = 'transform:rotate(-45deg) translate(5px,-5px)';
      } else {
        spans.forEach(s => s.removeAttribute('style'));
      }
    });
    // Close on outside click
    document.addEventListener('click', e => {
      if (!navbar.contains(e.target)) {
        mobileMenu.classList.remove('open');
        $$('span', hamburger).forEach(s => s.removeAttribute('style'));
        if (profileMenu) profileMenu.classList.remove('open');
      }
    });
  }

  // Profile Dropdown
  const profileBtn = document.getElementById('profileDropdownBtn');
  const profileMenu = document.getElementById('profileDropdownMenu');

  if (profileBtn && profileMenu) {
    profileBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      profileMenu.classList.toggle('open');
    });
  }
})();

/* ============================================
   SCROLL-REVEAL ANIMATIONS
   ============================================ */
(function initReveal() {
  const targets = $$('.post-card, .cat-card, .author-card, .trend-item, .stat-card, .float-card');
  if (!targets.length || !('IntersectionObserver' in window)) return;
  targets.forEach((el, i) => {
    el.style.cssText = 'opacity:0;transform:translateY(22px);transition:opacity .55s ease,transform .55s ease';
    el.style.transitionDelay = `${(i % 6) * 0.06}s`;
  });
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.opacity = '1';
        e.target.style.transform = 'translateY(0)';
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });
  targets.forEach(el => obs.observe(el));
})();

/* ============================================
   FOLLOW TOGGLE (Author cards, Profile)
   ============================================ */
function toggleFollow(btn, event) {
  if (event) event.stopPropagation();
  const isFollowing = btn.classList.contains('following');
  btn.classList.toggle('following', !isFollowing);
  btn.textContent = isFollowing ? 'Follow' : 'Following';
  showToast(isFollowing ? 'Unfollowed' : 'Following! ✓');
}

// Attach to all follow buttons
document.addEventListener('DOMContentLoaded', () => {
  $$('.follow-btn').forEach(btn => {
    btn.addEventListener('click', e => toggleFollow(btn, e));
  });
  $$('.follow-sm').forEach(btn => {
    btn.addEventListener('click', () => toggleFollow(btn));
  });
});

/* ============================================
   LIKE BUTTON (Blog Detail)
   ============================================ */
(function initLike() {
  const likeBtn = $('#likeBtn');
  const likeCount = $('#likeCount');
  if (!likeBtn || !likeCount) return;

  let count = parseInt(likeCount.textContent.replace(/[^0-9]/g, '')) || 0;
  let liked = false;

  likeBtn.addEventListener('click', () => {
    liked = !liked;
    likeBtn.classList.toggle('liked', liked);
    count = liked ? count + 1 : count - 1;
    likeCount.textContent = formatNumber(count);
    likeBtn.animate([
      { transform: 'scale(1)' },
      { transform: 'scale(1.18)' },
      { transform: 'scale(1)' }
    ], { duration: 220, easing: 'ease' });
    showToast(liked ? '♥ Added to your likes' : 'Removed from likes');
  });
})();

/* ============================================
   COMMENT SYSTEM (Blog Detail)
   ============================================ */
(function initComments() {
  const form = $('#commentForm');
  const textarea = $('#commentTextarea');
  const commentsList = $('#commentsList');
  if (!form || !textarea || !commentsList) return;

  form.addEventListener('submit', e => {
    e.preventDefault();
    const text = textarea.value.trim();
    if (!text) { showToast('Please write something first.', 'error'); return; }

    const comment = document.createElement('div');
    comment.className = 'comment';
    comment.style.animation = 'fadeUp .4s ease both';
    comment.innerHTML = `
      <div class="comment-avatar-wrap">
        <div class="avatar-placeholder avatar-sm" style="background:linear-gradient(135deg,#f093fb,#f5576c)">Y</div>
      </div>
      <div class="comment-content">
        <div class="comment-header">
          <strong>You</strong>
          <time>just now</time>
        </div>
        <p>${text.replace(/</g, '&lt;')}</p>
        <div class="comment-actions">
          <button class="comment-action-btn" onclick="this.textContent=this.textContent==='♥ 0'?'♥ 1':'♥ 0'">♥ 0</button>
          <button class="comment-action-btn" onclick="deleteComment(this)">Delete</button>
        </div>
      </div>`;
    commentsList.prepend(comment);
    textarea.value = '';
    showToast('Comment posted! ✓');

    const countEl = $('#commentCount');
    if (countEl) countEl.textContent = parseInt(countEl.textContent || 0) + 1;
  });
})();

function deleteComment(btn) {
  const comment = btn.closest('.comment');
  comment.style.opacity = '0';
  comment.style.transition = 'opacity .25s';
  setTimeout(() => comment.remove(), 260);
  showToast('Comment deleted');
}

/* ============================================
   EXPLORE FILTERS
   ============================================ */
(function initExploreFilters() {
  const chips = $$('.filter-chip');
  if (!chips.length) return;
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      $$('.post-card').forEach((card, i) => {
        card.style.opacity = '0';
        setTimeout(() => { card.style.opacity = '1'; card.style.transition = 'opacity .3s'; }, i * 40);
      });
    });
  });

  const searchInput = $('.search-wrap input');
  const searchBtn = $('.search-wrap button');
  if (searchInput && searchBtn) {
    searchBtn.addEventListener('click', () => {
      const q = searchInput.value.trim();
      if (q) { showToast(`Searching for "${q}"...`, 'info'); }
    });
    searchInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') searchBtn.click();
    });
  }
})();

/* ============================================
   PROFILE TABS
   ============================================ */
(function initProfileTabs() {
  const tabs = $$('.profile-tab');
  if (!tabs.length) return;
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const target = tab.dataset.tab;
      $$('[data-tab-content]').forEach(el => {
        el.style.display = el.dataset.tabContent === target ? '' : 'none';
      });
    });
  });
})();

/* ============================================
   CREATE POST / EDITOR
   ============================================ */
(function initEditor() {
  const titleInput = $('#postTitle');
  const editorBody = $('#editorBody');
  const seoTitle = $('#seoTitle');
  const seoDesc = $('#seoDesc');
  const saveStatus = $('#saveStatus');
  let saveTimer;

  function markUnsaved() {
    if (!saveStatus) return;
    saveStatus.textContent = 'Unsaved changes...';
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => { saveStatus.textContent = 'Draft auto-saved ✓'; }, 1800);
  }

  if (titleInput) {
    titleInput.addEventListener('input', () => {
      if (seoTitle) seoTitle.textContent = titleInput.value || 'Your story title...';
      markUnsaved();
    });
  }
  if (editorBody) {
    editorBody.addEventListener('input', () => {
      const words = editorBody.innerText.trim().split(/\s+/).slice(0, 22).join(' ');
      if (seoDesc) seoDesc.textContent = words + (editorBody.innerText.length > 120 ? '...' : '');
      markUnsaved();
    });
  }

  $$('.tb-btn[data-cmd]').forEach(btn => {
    btn.addEventListener('click', () => {
      if (!editorBody) return;
      editorBody.focus();
      const cmd = btn.dataset.cmd;
      if (cmd === 'insertOrderedList' || cmd === 'insertUnorderedList' || cmd === 'formatBlock') {
        document.execCommand(cmd, false, btn.dataset.val || null);
      } else {
        document.execCommand(cmd);
      }
      btn.classList.toggle('on');
    });
  });

  const fileInput = $('#coverFileInput');
  const uploadDrop = $('#uploadDrop');
  if (fileInput && uploadDrop) {
    uploadDrop.addEventListener('click', () => fileInput.click());
    uploadDrop.addEventListener('dragover', e => { e.preventDefault(); uploadDrop.style.borderColor = 'var(--accent)'; });
    uploadDrop.addEventListener('dragleave', () => uploadDrop.style.borderColor = '');
    uploadDrop.addEventListener('drop', e => {
      e.preventDefault();
      uploadDrop.style.borderColor = '';
      if (e.dataTransfer.files[0]) handleImageFile(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', () => { if (fileInput.files[0]) handleImageFile(fileInput.files[0]); });

    function handleImageFile(file) {
      if (!file.type.startsWith('image/')) { showToast('Please select an image file.', 'error'); return; }
      const reader = new FileReader();
      reader.onload = ev => {
        uploadDrop.innerHTML = `<img src="${ev.target.result}" style="width:100%;height:130px;object-fit:cover;border-radius:var(--r-sm)"><p style="font-size:.72rem;margin-top:8px;color:var(--ink-muted)">Click to replace</p>`;
      };
      reader.readAsDataURL(file);
    }
  }

  const tagWrap = $('#tagInputWrap');
  const tagField = $('#tagField');
  if (tagWrap && tagField) {
    tagField.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ',') {
        e.preventDefault();
        const val = tagField.value.replace(',', '').trim();
        if (val) addTag(val);
        tagField.value = '';
      }
    });
    tagWrap.addEventListener('click', () => tagField.focus());
  }

  const publishBtn = $('#publishBtn');
  const draftBtn = $('#draftBtn');
  if (publishBtn) {
    publishBtn.addEventListener('click', () => {
      const title = titleInput?.value?.trim();
      if (!title) { showToast('Please add a title before publishing.', 'error'); titleInput?.focus(); return; }
      publishBtn.textContent = 'Publishing...';
      publishBtn.style.opacity = '.7';
      setTimeout(() => {
        showToast('Story published! Redirecting... 🎉');
        setTimeout(() => window.location.href = 'blog-detail.html', 1500);
      }, 800);
    });
  }
  if (draftBtn) {
    draftBtn.addEventListener('click', () => {
      draftBtn.textContent = 'Saving...';
      setTimeout(() => { draftBtn.textContent = 'Save as Draft'; showToast('Draft saved ✓'); }, 700);
    });
  }
})();

function addTag(name) {
  const wrap = $('#tagInputWrap');
  const field = $('#tagField');
  if (!wrap || !field) return;
  const chip = document.createElement('div');
  chip.className = 'tag-item-chip';
  chip.innerHTML = `${name} <button onclick="this.parentElement.remove()" type="button">×</button>`;
  wrap.insertBefore(chip, field);
}

/* ============================================
   AUTH FORMS
   ============================================ */
(function initAuth() {
  const pwdInput = $('#passwordInput');
  const strengthBar = $('#strengthBar');
  if (pwdInput && strengthBar) {
    pwdInput.addEventListener('input', () => {
      const v = pwdInput.value;
      let score = 0;
      if (v.length >= 8) score++;
      if (/[A-Z]/.test(v)) score++;
      if (/[0-9]/.test(v)) score++;
      if (/[^A-Za-z0-9]/.test(v)) score++;
      const colors = ['#dc2626', '#f59e0b', '#10b981', '#059669'];
      const labels = ['Weak', 'Fair', 'Good', 'Strong'];
      strengthBar.style.width = (score * 25) + '%';
      strengthBar.style.background = colors[score - 1] || '#e5e7eb';
      const label = $('#strengthLabel');
      if (label) label.textContent = labels[score - 1] || '';
    });
  }

  $$('.form-input').forEach(input => {
    input.addEventListener('blur', () => {
      if (input.required && !input.value.trim()) {
        input.style.borderColor = '#dc2626';
      } else {
        input.style.borderColor = '';
      }
    });
    input.addEventListener('focus', () => { input.style.borderColor = ''; });
  });

  $$('.google-btn').forEach(btn => {
    btn.addEventListener('click', () => showToast('Google OAuth coming soon!', 'info'));
  });
})();

/* ============================================
   BLOG SHARE
   ============================================ */
(function initShare() {
  const shareBtn = $('#shareBtn');
  if (!shareBtn) return;
  shareBtn.addEventListener('click', async () => {
    if (navigator.share) {
      try {
        await navigator.share({ title: document.title, url: window.location.href });
      } catch (_) { }
    } else {
      await navigator.clipboard.writeText(window.location.href);
      showToast('Link copied to clipboard! ✓');
    }
  });
})();

/* ============================================
   SMOOTH SCROLL TO COMMENTS
   ============================================ */
document.addEventListener('click', e => {
  if (e.target.matches('[data-scroll-to]')) {
    const target = document.getElementById(e.target.dataset.scrollTo);
    if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
});

/* ============================================
   ACTIVE NAV LINK HIGHLIGHT
   ============================================ */
(function highlightNav() {
  const page = window.location.pathname.split('/').pop() || 'index.html';
  $$('.nav-links a').forEach(a => {
    if (a.getAttribute('href') === page) a.classList.add('active');
  });
})();