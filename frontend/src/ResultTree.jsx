import React, { useState } from 'react';
import { Narrator } from './Narrator.jsx';
import './ResultTree.css';

const findingTitles = {
  G01: 'Phí, cọc hoặc ký quỹ nhận/giữ việc',
  G02: 'Ứng vốn làm nhiệm vụ hoặc nộp thêm để rút tiền',
  G03: 'Ép mua gói hàng hoặc đứng tên vay',
  G04: 'Đòi OTP, mật khẩu hoặc dữ liệu định danh sinh trắc học',
  G05: 'Mở, cho thuê, bàn giao tài khoản hoặc chuyển tiền hộ',
  G06: 'Cài app lạ, chia sẻ màn hình hoặc điều khiển thiết bị',
  G07: 'Cưỡng ép, giữ giấy tờ, đòi ảnh nhạy cảm hoặc đe dọa',
  G08: 'Cảnh báo sớm: nhiệm vụ tương tác ảo / tin online mơ hồ',
};

function HighlightedText({ text, evidence }) {
  const fragments = [];
  let cursor = 0;

  // Backend offsets and JavaScript slice both count UTF-16 code units.
  for (const { id, start, end } of evidence) {
    fragments.push(text.slice(cursor, start));
    fragments.push(<mark key={id}>{text.slice(start, end)}</mark>);
    cursor = end;
  }
  fragments.push(text.slice(cursor));
  return <div className="dossier-original">{fragments}</div>;
}

export default function ResultTree({
  text, label, findings, sentences, caseTitle, explanations = {}, cases = [], possibleNextSteps = [],
}) {
  const codes = [...new Set(findings.map(finding => finding.code))];
  const [selected, setSelected] = useState(codes[0] ?? null);
  const evidenceIds = new Set(findings.filter(finding => finding.code === selected)
    .flatMap(finding => finding.evidenceSentenceIds));
  const evidence = sentences.filter(sentence => evidenceIds.has(sentence.id));
  const suspicious = label === 'suspicious';

  return (
    <div className="dossier-result">
      <section aria-labelledby="result-heading">
        <h1 id="result-heading" tabIndex={-1}>Bảng manh mối</h1>
        <Narrator mood={suspicious ? 'alert' : 'ok'}>
          {suspicious
            ? 'Tôi đã ghim các dấu hiệu tìm thấy bên dưới. Chạm vào từng ghim để đối chiếu câu được đánh dấu trong hồ sơ.'
            : 'Tôi đã đọc hồ sơ. Trong phần nội dung bạn gửi, tôi chưa tìm thấy câu nào khớp với các dấu hiệu đang kiểm tra.'}
        </Narrator>

        <div className="dossier-board">
          <article className="dossier-document">
            <span aria-hidden="true" className="dossier-pin" />
            <h2>{caseTitle || 'Hồ sơ của bạn'}</h2>
            <p className="dossier-document-label">Văn bản đã gửi</p>
            <HighlightedText text={text} evidence={evidence} />
          </article>

          {codes.length > 0 && (
            <ul className="dossier-clues" aria-label="Dấu hiệu phát hiện">
              {codes.map((code, index) => {
                const open = selected === code;
                const panelId = 'clue-detail-' + index;
                return (
                  <li key={code}>
                    <span aria-hidden="true" className="dossier-pin" />
                    <button type="button" aria-expanded={open} aria-controls={panelId}
                      onClick={() => setSelected(open ? null : code)}>
                      <span className="dossier-code">{code}</span>
                      <span>{findingTitles[code] ?? 'Dấu hiệu được phát hiện'}</span>
                      <span className="dossier-chevron" aria-hidden="true" />
                    </button>
                    <div id={panelId} hidden={!open}>
                      {open && <div className="dossier-detail">
                        <p className="dossier-quote-label">Đoạn hệ thống chú ý (tham khảo)</p>
                        {evidence.map(sentence => <blockquote key={sentence.id}>{sentence.text}</blockquote>)}
                        {explanations[code] && <p>{explanations[code]}</p>}
                      </div>}
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </section>

      {cases.length > 0 && (
        <section className="dossier-references" aria-labelledby="cases-heading">
          <h2 id="cases-heading">Vụ việc có thật</h2>
          {cases.map(item => (
            <article key={item.id}>
              <h3>{item.title}</h3>
              <p>{item.summary}</p>
              <ul aria-label="Điểm tương đồng">
                {Object.entries(item.matchReasons).map(([code, reason]) => (
                  <li key={code}><strong>{code}</strong> · {reason}</li>
                ))}
              </ul>
              <a href={item.sourceUrl} target="_blank" rel="noreferrer">Nguồn vụ việc</a>
            </article>
          ))}
        </section>
      )}

      {possibleNextSteps.length > 0 && (
        <section className="dossier-references" aria-labelledby="steps-heading">
          <h2 id="steps-heading">Diễn biến giả định</h2>
          <ul>
            {possibleNextSteps.map(step => (
              <li key={step.id}>{step.text} <a href={step.sourceUrl} target="_blank" rel="noreferrer">Nguồn tham khảo</a></li>
            ))}
          </ul>
        </section>
      )}

      <section className="dossier-conclusion" aria-labelledby="conclusion-heading">
        <h2 id="conclusion-heading">Kết luận</h2>
        <div className="dossier-stamp" data-alert={suspicious}>
          {suspicious ? 'Có dấu hiệu đáng ngờ' : 'Chưa phát hiện dấu hiệu'}
        </div>
      </section>
    </div>
  );
}
