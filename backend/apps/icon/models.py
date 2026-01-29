# models.py
class Icon(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название иконки")
    image = models.ImageField(
        upload_to='tournament_icons/',
        verbose_name="Файл иконки"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Иконка"
        verbose_name_plural = "Иконки"

    def __str__(self):
        return self.name
