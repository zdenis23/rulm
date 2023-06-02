BAD_SS = (
    " ул. ",
    " +7",
    "как ии",
    "как ai",
    "как аи",
    "как модель ии",
    "как алгоритм",
    "языковая модель ии",
    "как искусственный интеллект",
    "как нейросеть",
    "виртуальный ассистент",
    "виртуальный помощник",
    "как нейронная сеть",
    "онлайн-ассистент",
    "интеллектуальный помощник",
    "голосовой помощник",
    "искусственный разум",
    "компьютерная программа",
    "программный помощник",
    "представитель ии",
    "ассистент ии",
    "ии-ассистент",
    "умный искусственный интеллект",
    "помощник ai",
    "как ассистент",
    "как помощник",
    "как иси-ассистент"
    "ai помощник",
    "я являюсь искусственным интеллектом",
    "я искусственный интеллект",
    "я - искусственный интеллект",
    "я – искусственный интеллект",
    "я — искусственный интеллект",
    "я - искуственный интеллект",
    "в качестве ии",
    "в качестве искуственного интеллекта",
    "от лица ии",
    "от лица искуственного интеллекта",
    "openai",
    "chatgpt",
    "as a language model",
    "as an ai",
    "к сожалению",
    "sorry",
    "я - алгоритм",
    "я – алгоритм",
    "я - компьютерная программа",
    "я – компьютерная программа",
    "я компьютерная программа",
    "я являюсь компьютерной программой",
    "я - ai",
    "я – ai",
    "я ai",
    "я являюсь ai",
    "я - ии",
    "я – ии",
    "я ии",
    "я являюсь ии",
    "я - виртуальный помощник",
    "я – виртуальный помощник",
    "я виртуальный помощник",
    "я являюсь виртуальным помощником",
    "я - виртуальный ассистент",
    "я – виртуальный ассистент",
    "я виртуальный ассистент",
    "я являюсь виртуальным ассистентом",
    "я - программа",
    "я – программа",
    "я программа",
    "я являюсь программой",
    "я - ассистент",
    "я – ассистент",
    "я ассистент",
    "я - это искусственный интеллект",
    "я – это искусственный интеллект",
    "я – это искуственный интеллект",
    "я - это искуственный интеллект",
    "всего лишь искусственный интеллект",
    "всего лишь искуственный интеллект"
)

def has_bad_ss(messages):
    for m in messages:
        text = m["content"].lower()
        if any(ss in text for ss in BAD_SS):
            return True
    return False
