import React from 'react';
import { Detective } from './Narrator.jsx';
import './DetectiveLoading.css';

export default function DetectiveLoading({ text }) {
  return <section className="loading-case page-shell" role="status" aria-labelledby="analysis-loading-title">
    <h1 id="analysis-loading-title">Đang kiểm tra nội dung…</h1>
    <div className="case-desk loading-desk" aria-hidden="true">
      <div><p className="thought">Để tôi xem kỹ hồ sơ này…</p><Detective /></div>
      <div className="loading-file"><small>HỒ SƠ ĐANG ĐỌC</small><p>{text.slice(0, 450)}</p></div>
    </div>
  </section>;
}
