import streamlit as st
import pandas as pd
import pickle
import sklearn

# Загрузка модели
@st.cache_resource
def load_model():
    with open('xgb_classifier.pkl', 'rb') as f:
        return pickle.load(f)

model = load_model()

st.title ("🔮Предсказание оттока клиентов")

# Drug & Drop загрузка файла
uploaded_file = st.file_uploader("Перетащите сюда файл Excel/csv с данными клиента",
                                type=['xlsx', 'csv'])

if uploaded_file:
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    elif uploaded_file.name.endswith('.csv'): 
        df = pd.read_csv(uploaded_file)
    else:
        pass
    st.write("Данные загружены!")
    
    # Предобразование данных для модели
    df['Date'] = pd.to_datetime(df['Date'])
    df['Day'] = df['Date'].dt.day
    df['Month'] = df['Date'].dt.month
    df['Year'] = df['Date'].dt.year
    
    new_names = ["ИД", "АЗС", "Оператор", "Сопутствующий товар", "Нефтепродукт", "Вид оплаты", "Тип транзакции",
              "Контрагент", "№ бонусной карты", "№ чека", "Цена", "Скидка", "Бонусов начислено", "Бонусов списано",
              "Остаток бонусов", "Кол-во (только для СТ)", "Объем (только для НП)", "Масса (только для НП)",
              "Время суток", "Дата", "День", "Месяц", "Год"]
    # Переименование столбцов
    df.columns = new_names

    # Представим время транзакции в секундах, это нужно для выражения данных этого столбца в цисленных значениях, а не типа "datetime"
    df['Время суток секунды'] = df['Время суток'].apply(lambda x: int(x.split(':')[0]) * 3600
                                                                               + int(x.split(':')[1]) * 60 + int(x.split(':')[2]))
    df['Время суток часы'] = df['Время суток секунды'] / 3600
    df.drop('Время суток', axis=1, inplace=True)

    # Отбор признаков для модели и переименование в соответствии с моделью
    df = df[['Оператор', 'Цена', 'Нефтепродукт', 'Вид оплаты', 'Тип транзакции', 'Объем (только для НП)', 'Время суток часы']]
    df.columns = ['Последний(ая) Оператор перед оттоком', 'Последний(ая) Цена перед оттоком', 'Последний(ая) Нефтепродукт перед оттоком',
              'Последний(ая) Вид оплаты перед оттоком', 'Последний(ая) Тип транзакции перед оттоком', 'Последний(ая) Объем (только для НП) перед оттоком',
              'Последний(ая) Время суток часы перед оттоком']
    
    st.dataframe(df)
   
# Предсказание
if st.button("Предсказать отток"):
    prediction = model.predict(df)
    probability = model.predict_proba(df)

    if prediction[0] == 1:
        st.error(f"🆘Высокий риск оттока (вероятность оттока: {probability[0][1]: .2%)}")
    elif prediction[0] == 0:
        st.success(f"🎉Низкий риск оттока (вероятность оттока: {probability[0][0]: .2%}")
    else:
        st.write("Сначала загрузите данные!")



















