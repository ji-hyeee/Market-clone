const form = document.getElementById("write-form");

const handleSubmitForm = async (event) => {
  event.preventDefault();

  // 현재시간 보내주기
  const body = new FormData(form);
  body.append("insertAt", new Date().getTime());

  // 에러 처리
  try {
    const res = await fetch("/items", {
      method: "POST",
      body
    });

    const data = await res.json();
    // 페이지 이동
    if (data === '200') window.location.pathname = "/";
  } catch (e) {
    console.error(e);
  }
};

form.addEventListener("submit", handleSubmitForm);