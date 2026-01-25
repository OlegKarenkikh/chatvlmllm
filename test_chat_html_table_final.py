#!/usr/bin/env python3
"""
Финальный тест HTML таблиц в чате - симуляция реального сценария
"""

import streamlit as st
from utils.smart_content_renderer import SmartContentRenderer

def simulate_chat_message():
    """Симуляция сообщения чата с HTML таблицей"""
    
    # Точно такой же контент, как сообщил пользователь
    message_content = """📋 Детальная информация<table class="bbox-table">         <thead>             <tr>                 <th style="width: 50px;">#</th>                 <th style="width: 150px;">Категория</th>                 <th style="width: 200px;">BBOX координаты</th>                 <th>Текст</th>             </tr>         </thead>         <tbody>             <tr>                 <td>1</td>                 <td>Заголовок документа</td>                 <td>[45, 123, 567, 189]</td>                 <td>ВОДИТЕЛЬСКОЕ УДОСТОВЕРЕНИЕ</td>             </tr>             <tr>                 <td>2</td>                 <td>Персональные данные</td>                 <td>[78, 234, 456, 298]</td>                 <td>ИВАНОВ ИВАН ИВАНОВИЧ</td>             </tr>             <tr>                 <td>3</td>                 <td>Дата рождения</td>                 <td>[123, 345, 389, 412]</td>                 <td>15.03.1985</td>             </tr>             <tr>                 <td>4</td>                 <td>Место рождения</td>                 <td>[156, 456, 678, 523]</td>                 <td>г. Москва</td>             </tr>         </tbody>     </table>

Анализ завершен. Найдено 4 текстовых блока с координатами."""

    return {
        "role": "assistant",
        "content": message_content
    }

def main():
    st.title("💬 Тест HTML таблиц в чате")
    st.write("Симуляция реального сценария из чата пользователя")
    
    # Создаем сообщение
    message = simulate_chat_message()
    
    st.subheader("🔍 Исходный контент:")
    with st.expander("Показать исходный HTML"):
        st.code(message["content"])
    
    st.divider()
    
    # Симулируем отображение в чате
    st.subheader("💬 Как отображается в чате:")
    
    with st.chat_message("assistant"):
        try:
            # Используем тот же метод, что и в реальном приложении
            SmartContentRenderer.render_content_smart(message["content"])
            
        except Exception as e:
            st.error(f"❌ Ошибка рендеринга: {e}")
            st.exception(e)
    
    st.divider()
    
    # Проверка определения HTML
    st.subheader("🧪 Диагностика:")
    
    has_html = SmartContentRenderer.has_html_content(message["content"])
    st.write(f"**HTML обнаружен:** {has_html}")
    
    if has_html:
        content_info = SmartContentRenderer.extract_html_and_text(message["content"])
        st.write(f"**Найдено таблиц:** {len(content_info['tables'])}")
        st.write(f"**Текст без таблиц:** {len(content_info['text_content'])} символов")
        
        if content_info['tables']:
            st.success("✅ Таблица успешно извлечена и должна отображаться корректно")
        else:
            st.error("❌ Таблица не найдена")
    else:
        st.error("❌ HTML не обнаружен")
    
    st.divider()
    
    # Для сравнения - старый способ
    st.subheader("📝 Для сравнения - обычный markdown:")
    st.markdown(message["content"])

if __name__ == "__main__":
    main()