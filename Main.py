import pygame
import sys  # Модуль sys нужен для корректного выхода из программы

def main():
    # Инициализация pygame
    pygame.init()
    
    # Настройки окна
    WINDOW_WIDTH = 640
    WINDOW_HEIGHT = 700
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Болотуда")
    
    # Частота обновления экрана
    FPS = 60
    clock = pygame.time.Clock()
    
    # Импорт классов из других модулей
    from game import Game
    
    try:
        # Создание экземпляра игры
        game = Game(window)
        
        # Основной игровой цикл
        running = True
        while running:
            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Передаем позицию клика в игру
                    game.handle_click(pygame.mouse.get_pos())
            
            # Обновление состояния игры
            game.update()
            
            # Обновление экрана
            pygame.display.flip()
            
            # Ограничение FPS
            clock.tick(FPS)
            
    except Exception as e:
        # Вывод ошибок в консоль
        print(f"Произошла ошибка: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Завершение работы pygame
        pygame.quit()
        # Выход из программы (sys.exit() гарантирует завершение всех потоков)
        sys.exit()

# Запуск игры только если файл выполняется напрямую
if __name__ == "__main__":
    main()