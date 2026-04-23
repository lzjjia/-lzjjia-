#全局状态定义


from typing import TypedDict, List, Any
class StudentProfile(TypedDict):
    name: str
    learning_style: str
    energy_pattern: str
    current_courses: List[str]
    challenge: List[str]

class AtlasState(TypedDict):
    #学生信息
    student_profile: StudentProfile
    user_input: str
    #各agent输出
    coordinator: str #协调者的路由决策
    study_schedule: str #计划者生成的时间表
    study_notes: str #笔记者生成的学习材料
    advisor_feedback: str #顾问的反馈信息
    #对话历史
    messages: List[dict]
    final_response: str 
    #工作流的控制
    next_agent: str
    iteration: int
    callbacks: List[Any]
