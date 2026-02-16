/**
 * 게시판 공통 스크립트
 * 탭 전환, 검색 placeholder 등 UI 동작 처리
 */

(function () {
  'use strict';

  /**
   * DOM 로드 완료 후 초기화
   */
  document.addEventListener('DOMContentLoaded', function () {
    initBoardTabs();
    initBoardSearch();
  });

  /**
   * 탭 전환 처리 (현재 페이지 기준 활성 탭 표시)
   * 실제 활성 상태는 HTML의 board-tabs__item--active 클래스로 제어
   */
  function initBoardTabs() {
    const tabs = document.querySelectorAll('.board-tabs__item');
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function (e) {
        // 링크 기본 동작 유지 (페이지 이동)
        // 추후 SPA 전환 시 e.preventDefault() 후 AJAX 로드 가능
      });
    });
  }

  /**
   * 검색 입력 필드 포커스/블러 시 placeholder 동작
   * (추가 동작 필요 시 확장)
   */
  function initBoardSearch() {
    const searchInputs = document.querySelectorAll('.board-search__input');
    searchInputs.forEach(function (input) {
      input.addEventListener('focus', function () {
        input.classList.add('board-search__input--focused');
      });
      input.addEventListener('blur', function () {
        input.classList.remove('board-search__input--focused');
      });
    });
  }
})();
