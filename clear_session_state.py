#!/usr/bin/env python3
"""
Скрипт для очистки session_state в Streamlit приложении
Решает проблему с кешированием старых экземпляров менеджера
"""

import streamlit as st

def clear_session_state():
    """Очистка всех кешированных объектов"""
    
    st.title("🔄 Очистка Session State")
    
    if st.button("🗑️ Очистить все кешированные объекты", type="primary"):
        
        # Список ключей для очистки
        keys_to_clear = [
            "single_container_manager",
            "vllm_adapter", 
            "model_loader",
            "loaded_models"
        ]
        
        cleared_count = 0
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
                cleared_count += 1
                st.success(f"✅ Очищен: {key}")
        
        if cleared_count > 0:
            st.success(f"🎉 Очищено объектов: {cleared_count}")
            st.info("💡 Теперь перейдите в основное приложение - будут созданы новые экземпляры с исправленным кодом")
        else:
            st.info("ℹ️ Session state уже пуст")
    
    # Показываем текущее содержимое session_state
    st.subheader("📊 Текущее содержимое Session State")
    
    if st.session_state:
        for key, value in st.session_state.items():
            st.write(f"**{key}**: {type(value).__name__}")
    else:
        st.write("Session state пуст")

if __name__ == "__main__":
    clear_session_state()