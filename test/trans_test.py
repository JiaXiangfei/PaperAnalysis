from utils.Translate import *
text = r'E:\aaa项目\研究生\2024-3大模型论文摘取\工程化\PaperRecommmend\output\KDD_zhanglin_Getting_LLM_to_think_and_act_like_a_human_being__Logical_path_reasoning_and_Replanning\text_parts.json'
images_insert_txt_path = r'E:\aaa项目\研究生\2024-3大模型论文摘取\工程化\PaperRecommmend\output\KDD_zhanglin_Getting_LLM_to_think_and_act_like_a_human_being__Logical_path_reasoning_and_Replanning\images_insert.txt'
images_insert_json_path = r'E:\aaa项目\研究生\2024-3大模型论文摘取\工程化\PaperRecommmend\output\KDD_zhanglin_Getting_LLM_to_think_and_act_like_a_human_being__Logical_path_reasoning_and_Replanning\images_insert.json'
image_tag = r"<(\d+)>"

test = """
<5>triggers.
"""


# result_cn = translate(text, images_insert_txt_path, images_insert_json_path, image_tag)
extract_and_translate(test, image_tag)