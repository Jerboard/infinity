 // Получаем все элементы форм на странице
  const forms = document.getElementsByTagName('form');

  // Обрабатываем событие нажатия клавиши
  document.addEventListener('keydown', function(event) {
    // Проверяем, нажата ли клавиша Enter (код клавиши 13)
    if (event.key === 'Enter' || event.keyCode === 13) {
      // Перебираем все формы
      Array.from(forms).forEach(function(form) {
        // Получаем элементы ввода внутри формы
        const inputs = form.querySelectorAll('input');

        // Проверяем, заполнены ли оба поля ввода
        const filled = Array.from(inputs).every(function(input) {
          return input.value.trim() !== '';
        });

        // Если оба поля заполнены, отправляем форму
        if (filled) {
          form.submit();
        }
      });
    }
  });