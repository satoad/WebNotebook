const usernameElement = document.getElementById("authorized");
const loginButton = document.getElementById("unauthorized");

// Проверяем, авторизован ли пользователь
const isAuthorized = true; // Здесь должна быть логика проверки авторизации

// Функция для обновления отображения элементов на странице
function updateUI() {
  if (isAuthorized) {
    // Если пользователь авторизован, показываем его имя и скрываем кнопку "Войти"
    const username = "User 01"; // Здесь должно быть получение имени пользователя
    usernameElement.firstChild.textContent = username;
    loginButton.style.display = "none";
  } else {
    // Если пользователь не авторизован, скрываем имя пользователя и показываем кнопку "Войти"
    usernameElement.style.display = "none";
    loginButton.style.display = "block";
  }
}

updateUI();
