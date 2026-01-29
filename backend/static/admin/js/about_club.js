document.addEventListener("DOMContentLoaded", function () {
    // Обработчик для всех существующих и будущих file inputs
    document.addEventListener('change', function(event) {
        if (event.target.type === 'file') {
            updatePreview(event.target);
        }
    });

    function updatePreview(input) {
        const row = input.closest('tr');
        const previewCell = row.querySelector('.field-image_preview');

        if (!previewCell) return;

        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                // Очищаем ячейку и создаём новое изображение
                previewCell.innerHTML = '';
                const img = document.createElement('img');
                img.src = e.target.result;
                img.style.width = '100px';
                img.style.height = '100px';
                img.style.objectFit = 'cover';
                img.style.borderRadius = '4px';
                previewCell.appendChild(img);
            }
            reader.readAsDataURL(input.files[0]);
        } else {
            // Если файл убран — показываем текст
            previewCell.innerHTML = '<span style="color:#999;">Нет изображения</span>';
        }
    }

    // Также обрабатываем существующие inputs при загрузке
    document.querySelectorAll('input[type=file]').forEach(function(input){
        // Уже обрабатываются через делегирование, но на всякий случай
        input.addEventListener('change', function() {
            updatePreview(input);
        });
    });
});