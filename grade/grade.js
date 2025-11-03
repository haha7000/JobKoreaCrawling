/* =========================
 * 보험 영업직 채용 평가 (총점 100)
 * 입력:  User_Data
 * 출력:  User_Data_Score_Only  (원본 주요 필드 + score만)
 * ========================= */

// ---------- 키워드 사전 ----------
var KW = {
    insuranceSales: ["보험 영업","보험영업","보험상품","설계사","FP","GA","생명보험","손해보험","보장 분석","보장설계","종합재무설계","리모델링"],
    financeSales: ["금융 영업","금융상품","자산관리","PB","WM","펀드","증권","투자","대출상담","카드영업","지점 영업"],
    generalSales: ["영업","세일즈","판매","B2B 영업","B2C 영업","영업관리","상담원","상담","텔레마케팅","TM","영업지원","영업기획","고객유치","가망고객","리드","콜"],
    indirectSales: ["고객응대","CS","시장조사","프로모션","홍보","행사 운영","매장관리","판촉"],
    activity: ["동아리","인턴","대외활동","프로젝트","공모전","서포터즈","홍보대사"],
    commStrong: ["고객 니즈","니즈 파악","경청","문제 해결","클레임","VOC","고객 만족","재구매","추천","관계 형성","관계관리","상담 스크립트","컨설팅","제안","설득"],
    commMedium: ["소통","협업","커뮤니케이션","팀워크","협력","친화력","긍정","배려","설명"],
    certHigh: ["손해사정사","AFPK","CFP","투자자산운용사","증권투자권유대행인","파생상품투자권유자문인력","보험계리사"],
    certBasic: ["보험 모집인","생명보험 모집인","손해보험 모집인","펀드투자권유대행인","펀드투자상담사","은행FP","퇴직연금","신용분석사"],
    certLight: ["운전면허","2종보통","1종보통","CS리더스","MOS"],
    majorFinance: ["금융","경제","경영","보험","재무","회계","금융공학","보험계리","비즈니스"],
    eduFinance: ["금융 교육","펀드 교육","자산관리 교육","세일즈 교육","세일즈 트레이닝","상담 스킬","세일즈 아카데미","콜 교육","FP 교육"],
    motiveStrong: ["보험 산업","보험업","GA 채널","모집질서","준법","소비자보호","보장분석","리드관리","고객발굴","리텐션","리쿠르팅","월납","보장성","인바운드/아웃바운드","컨설팅영업"],
    motiveWeak: ["성장","열정","도전","문제 해결","목표","성과","책임감","자기계발"],
    langNames: ["TOEIC","토익","OPIC","OPIc","오픽","TOEFL","IELTS"]
  };
  
  // 수치/어학 패턴
  var RX = {
    numberHit: /(\d{2,}\s*(%|건|명|회|개|만원|억|개월|주|일))|(\+\d{1,}%)/i,
    toeic: /(TOEIC|토익)\s*[:\-]?\s*(\d{3,4})/i,
    opic: /(OPIC|OPIc|오픽)\s*[:\-]?\s*([AIL]\w?)/i
  };
  
  // 유틸
  function toStr(x){ return x == null ? "" : String(x); }
  function arr(v){ return Array.isArray(v) ? v : (v==null?[]:[v]); }
  function norm(s){ return toStr(s).toLowerCase().replace(/\s+/g," ").trim(); }
  function bagJoin(list){
    var out = [];
    for (var i=0;i<list.length;i++){
      var v = list[i];
      if (v==null) continue;
      out.push(Array.isArray(v)? v.join(" "): String(v));
    }
    return out.join(" | ");
  }
  function hasAny(text, kws){
    var T = norm(text);
    for (var i=0;i<kws.length;i++){
      if (T.indexOf(norm(kws[i])) !== -1) return true;
    }
    return false;
  }
  function findOpicLevel(s){ var m = toStr(s).match(RX.opic); return m ? (m[2]||"").toUpperCase() : ""; }
  function findToeicScore(s){ var m = toStr(s).match(RX.toeic); return m ? parseInt(m[2],10) : NaN; }
  function max(a,b){ return a>b ? a : b; }
  
  // --- 항목별 스코어러 ---
  function scoreSalesExp(u){
    var expText = bagJoin([u["경력요약"], u["경력상세"], u["인턴대외활동요약"], u["인턴대외활동상세"], u["title"], u["career"], u["skills"]]);
    var actHit = hasAny(expText, KW.activity) || RX.numberHit.test(expText);
  
    var base = 0;
    if (hasAny(expText, KW.insuranceSales) || hasAny(expText, KW.financeSales)) base = 20;
    else if (hasAny(expText, KW.generalSales)) base = 15;
    else if (hasAny(expText, KW.indirectSales)) base = 10;
  
    var activity = actHit ? (RX.numberHit.test(expText) ? 5 : 3) : 0;
    var exp25 = Math.min(25, base + activity);
  
    var jobField = toStr(u["지원분야_직무"]);
    var job5 = 0;
    if (hasAny(jobField, [].concat(KW.insuranceSales, KW.financeSales))) job5 = 5;
    else if (hasAny(jobField, KW.generalSales)) job5 = 3;
  
    return { subtotal: exp25 + job5 };
  }
  
  function scoreCustomerComm(u){
    // 자기소개서 제거됨
    var comm20 = 0;

    var fit5 = 0;
    var fitText = toStr(u["인재상"]);
    if (hasAny(fitText, ["고객 중심","관계","소통","긍정","신뢰"])) fit5 = 5;
    else if (fitText) fit5 = 3;

    return { subtotal: comm20 + fit5 };
  }
  
  function scoreSpecialization(u){
    var certText = bagJoin([u["자격증요약"], u["자격증상세"], u["skills"]]);
    var eduText  = bagJoin([u["학력상세"], u["교육상세"], u["education"], u["title"]]);
  
    var cert20 = 0;
    if (hasAny(certText, KW.certHigh)) cert20 = 20;
    else if (hasAny(certText, KW.certBasic)) cert20 = 10;
    else if (hasAny(certText, KW.certLight)) cert20 = 2;
  
    var edu10 = 0;
    if (hasAny(eduText, KW.majorFinance) || hasAny(eduText, KW.eduFinance)) edu10 = 10;
    else if (hasAny(eduText, ["경제원론","재무회계","마케팅","금융상품"])) edu10 = 5;
  
    return { subtotal: cert20 + edu10 };
  }
  function scoreMotivationAndLang(u){
    // 자기소개서 제거됨
    var lang   = bagJoin([u["어학요약"], u["어학능력상세"], u["skills"]]);

    var mot10 = 0;

    var lang5 = 0, toeic = findToeicScore(lang), opic = findOpicLevel(lang);
    if (!isNaN(toeic)){
      if (toeic >= 900) lang5 = 5;
      else if (toeic >= 700) lang5 = 3;
      else if (toeic >= 600) lang5 = 1;
    }
    if (lang5 === 0 && opic){
      if (/AL|IH/.test(opic)) lang5 = 5;
      else if (/IM/.test(opic)) lang5 = 3;
      else lang5 = 1;
    }
    if (lang5 === 0 && hasAny(lang, KW.langNames)) lang5 = 1;

    return { subtotal: mot10 + lang5 };
  }
  
  // --- 메인: score만 붙인 딕셔너리 ---
  (function(){
    var src = (typeof User_Data !== "undefined" && User_Data) ? User_Data : {};
    var FIELDS = ["index","name","gender","age","career","title","education","region","skills"];
  
    var out = {};
    Object.keys(src).sort(function(a,b){return (parseInt(a,10)||0) - (parseInt(b,10)||0);})
    .forEach(function(k){
      var u = src[k] || {};
  
      var total =
        scoreSalesExp(u).subtotal +
        scoreCustomerComm(u).subtotal +
        scoreSpecialization(u).subtotal +
        scoreMotivationAndLang(u).subtotal;  // 총점 100
  
      var row = {};
      FIELDS.forEach(function(f){
        var v = u[f];
        row[f] = (v==null ? (f==="skills"? []:"") : v);
      });
      row.score = total;
  
      out[k] = row;
    });
  
    User_Data_Score_Only = out;  // 전역 결과
    RESULT = "ok | scored=" + Object.keys(out).length;
  })();
  