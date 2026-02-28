/**
 * 게시판 공통 스크립트
 * 탭 전환, 검색 Enter 키 이벤트 처리
 */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    initBoardTabs();
    initBoardSearch();
    initCourseSearch();
    initCommunitySearch();
  });

  /**
   * 탭 전환 처리 (링크 기본 동작 유지)
   */
  function initBoardTabs() {
    var tabs = document.querySelectorAll('.board-tabs__item');
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        // 링크 기본 동작 유지 (페이지 이동)
      });
    });
  }

  /**
   * 검색 입력 필드 포커스/블러 시 스타일 처리
   */
  function initBoardSearch() {
    var searchInputs = document.querySelectorAll('.board-search__input');
    searchInputs.forEach(function (input) {
      input.addEventListener('focus', function () {
        input.classList.add('board-search__input--focused');
      });
      input.addEventListener('blur', function () {
        input.classList.remove('board-search__input--focused');
      });
    });
  }

  /**
   * 강의평가 검색 (교수명 + 과목명)
   * Enter 키 → ?professor=...&subject=... 로 이동
   * 현재 탭(cat) 파라미터는 없음 (강의평가는 board_id=1 고정)
   */
  function initCourseSearch() {
    var profInput    = document.getElementById('searchProfessor');
    var subjectInput = document.getElementById('searchSubject');
    if (!profInput && !subjectInput) return;

    function doCourseSearch() {
      var prof    = profInput    ? profInput.value.trim()    : '';
      var subject = subjectInput ? subjectInput.value.trim() : '';
      var params  = new URLSearchParams();
      if (prof)    params.set('professor', prof);
      if (subject) params.set('subject',   subject);
      var qs = params.toString();
      window.location.href = '/board/course' + (qs ? '?' + qs : '');
    }

    [profInput, subjectInput].forEach(function (el) {
      if (!el) return;
      el.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') doCourseSearch();
      });
    });
  }

  /**
   * 커뮤니티 검색 (키워드)
   * Enter 키 → ?cat=현재탭&q=키워드 로 이동
   */
  function initCommunitySearch() {
    var keywordInput = document.getElementById('searchKeyword');
    if (!keywordInput) return;

    // 현재 탭(cat) URL 파라미터 읽기
    var currentCat = new URLSearchParams(window.location.search).get('cat') || 'anonymous';

    keywordInput.addEventListener('keydown', function (e) {
      if (e.key !== 'Enter') return;
      var q      = keywordInput.value.trim();
      var params = new URLSearchParams({ cat: currentCat });
      if (q) params.set('q', q);
      window.location.href = '/board/community?' + params.toString();
    });
  }

})();
