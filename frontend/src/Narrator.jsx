import React from 'react';

const BROW = { think: ['M57 58 Q64 55 72 57', 'M78 57 Q86 55 93 58'], alert: ['M56 54 L72 61', 'M78 61 L94 54'], ok: ['M57 57 Q64 54 72 56', 'M78 56 Q86 54 93 57'] }
const MOUTH = { think: 'M68 91 L82 91', alert: 'M67 95 Q75 86 83 95', ok: 'M67 89 Q75 97 83 89' }

export function Detective({ mood = 'think', portrait = false }) {
  return (
    <svg className={portrait ? 'soi-portrait' : 'soi-figure'} viewBox={portrait ? '30 14 90 88' : '0 0 150 210'} aria-hidden="true">
<ellipse cx="75" cy="207" rx="42" ry="4" fill="rgba(0,0,0,.3)" />
        <rect x="52" y="165" width="16" height="38" fill="#1c3a6b" /><rect x="82" y="165" width="16" height="38" fill="#1c3a6b" />
        <ellipse cx="58" cy="204" rx="14" ry="5" fill="#0b1b36" /><ellipse cx="92" cy="204" rx="14" ry="5" fill="#0b1b36" />
        {/* tay trái buông */}
        <path d="M46 114 L36 152" stroke="#a07e45" strokeWidth="13" strokeLinecap="round" /><circle cx="36" cy="156" r="6.5" fill="#f2c9a0" />
        {/* áo choàng */}
        <path d="M36 182 L47 108 Q75 96 103 108 L114 182 Z" fill="#c8a165" />
        <path d="M75 112 L75 182" stroke="#a07e45" strokeWidth="2" />
        <rect x="42" y="144" width="66" height="7" fill="#8a6a36" /><rect x="70" y="143" width="10" height="9" rx="1.5" fill="#e6c36b" />
        <circle cx="68" cy="124" r="2" fill="#8a6a36" /><circle cx="82" cy="124" r="2" fill="#8a6a36" /><circle cx="68" cy="166" r="2" fill="#8a6a36" /><circle cx="82" cy="166" r="2" fill="#8a6a36" />
        <path d="M63 104 L75 124 L87 104 Z" fill="#f4f1ea" /><path d="M73 110 L77 110 L79 130 L75 137 L71 130 Z" fill="#b91c1c" />
        <path d="M54 106 L66 101 L75 124 L58 120 Z" fill="#b8914f" /><path d="M96 106 L84 101 L75 124 L92 120 Z" fill="#b8914f" />
        {/* đầu */}
        <circle cx="49" cy="73" r="5" fill="#f2c9a0" /><circle cx="101" cy="73" r="5" fill="#f2c9a0" />
        <circle cx="75" cy="71" r="27" fill="#f2c9a0" />
        <circle cx="75" cy="80" r="3.3" fill="#e3a97c" />
        <ellipse cx="65" cy="70" rx="7.5" ry="8.5" fill="#fff" /><ellipse cx="85" cy="70" rx="7.5" ry="8.5" fill="#fff" />
        <g className="soi-eyes">
          <circle cx="65" cy="70" r="3.8" fill="#10264a" /><circle cx="85" cy="70" r="3.8" fill="#10264a" />
          <circle cx="66.2" cy="68.6" r="1.1" fill="#fff" /><circle cx="86.2" cy="68.6" r="1.1" fill="#fff" />
        </g>
        <path d={BROW[mood][0]} stroke="#3b2a1a" strokeWidth="3" strokeLinecap="round" fill="none" />
        <path d={BROW[mood][1]} stroke="#3b2a1a" strokeWidth="3" strokeLinecap="round" fill="none" />
        <path d={MOUTH[mood]} stroke="#7a3b2e" strokeWidth="2.6" strokeLinecap="round" fill="none" />
        {/* mũ phớt */}
        <ellipse cx="75" cy="50" rx="42" ry="8" fill="#10264a" />
        <path d="M47 50 Q47 20 75 20 Q103 20 103 50 Z" fill="#1c3a6b" />
        <path d="M60 22 Q75 30 90 22" stroke="#10264a" strokeWidth="3" fill="none" />
        <path d="M47 50 L47 42 Q75 48 103 42 L103 50 Q75 56 47 50 Z" fill="#0d9488" />
            {!portrait && <g className="soi-glass">
        <path d="M102 113 Q113 145 125 113" stroke="#b48f54" strokeWidth="12" fill="none" strokeLinecap="round" />
        <path d="M126 117 l12 -24" stroke="#593e27" strokeWidth="6" strokeLinecap="round" />
        <circle cx="124" cy="116" r="6" fill="#f2c9a0" />
        <circle cx="139" cy="87" r="10" fill="#a5f3fc" fillOpacity=".65" stroke="#254c67" strokeWidth="4" />
      </g>}
    </svg>
  );
}

export function Narrator({ mood = 'think', children }) {
  return <div className="soi-narrator"><Detective mood={mood} portrait />
    <div><strong>Thám tử Soi</strong><p>{children}</p></div>
  </div>;
}
