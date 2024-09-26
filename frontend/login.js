const form = document.querySelector("#login-form");

// let accessToken = null;

const handleSubmit = async (event) => {
  event.preventDefault();
  const formData = new FormData(form);
  const sha256Password = sha256(formData.get("password"));
  formData.set("password", sha256Password);

  const res = await fetch("/login", {
    method: "POST",
    body: formData
  });

  const data = await res.json();
  const accessToken = data.access_token;
  // 로컬스토리지 
  window.localStorage.setItem("token", accessToken);
  alert("로그인 성공~")
  // 세션스토리지
  // window.sessionStorage.setItem("token", accessToken);

  // const infoDiv = document.querySelector("#info");
  // infoDiv.innerText = "로그인 성공!!!";

  window.location.pathname = "/";

  // const btn = document.createElement("button");
  // btn.innerText = "상품 가져오기";
  // btn.addEventListener("click", async () => {
  //   const res = await fetch("/items", {
  //     headers: {
  //       "Authorization": `Bearer ${accessToken}`,
  //     },
  //   });
  //   const data = await res.json();
  //   console.log(data);
  // });
  // infoDiv.appendChild(btn);

  // if (res.status === 200) {
  //   alert("로그인 성공!!!");
  //   window.location.pathname = "/";
  // } else if (res.status === 401) {
  //   alert("아이디 혹은 비밀번호가 맞지 않습니다");;
  // }
};

form.addEventListener("submit", handleSubmit);