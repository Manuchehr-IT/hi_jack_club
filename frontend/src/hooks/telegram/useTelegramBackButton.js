import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export function useTelegramBackButton(enabled = true) {
  const navigate = useNavigate()

  useEffect(() => {
    const tg = window.Telegram?.WebApp
    if (!tg) return

    if (enabled) {
      tg.BackButton.show()
    } else {
      tg.BackButton.hide()
    }

    const handleBack = () => {
      if (window.history.length > 1) {
        navigate(-1)
      } else {
        tg.close()
      }
    }

    tg.BackButton.onClick(handleBack)

    return () => {
      tg.BackButton.offClick(handleBack)
      tg.BackButton.hide()
    }
  }, [enabled, navigate])
}
