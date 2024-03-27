import json
from datetime import datetime

class CustomDatasetMaker():
    def __init__(self, ConsultationDataPath, ExpertDataPath, StudentList):
        with open(ConsultationDataPath, "r") as f:
            self.Consultation = json.load(f)
            
        with open(ExpertDataPath, "r") as f:
            self.Expert = json.load(f)
        
        self.StudentList = StudentList
        
    def __call__(self):
        data_set = []
        for i in self.StudentList:
            data_set.append(self.make_Data(i))
        
        return data_set
    
    def get_Consultation_contents(self, idx:str): # 수정 필요 ( 학생 id로 상담 내용을 가져와야 한다. 한 학생당 보통 2개의 상담 데이터가 있고 그 이상일 수 있다. )
        consultation = ""
        for cons in self.Consultation:
            if self.Consultation[cons]['meta']['student_idx'] == idx:
                for conv in self.Consultation[cons]['conversation']:
                    if not conv['conv_category'] == "기타" :
                        for spk in conv['utterances']:
                            consultation += spk['utterance'] + "\n"
        return consultation
    
    def get_response(self, idx:str): # 전문가 총평에 대한건 한 학생당 한 개씩 있다. 
        for i in self.Expert:
            if self.Expert[i]['student_idx'] == idx:
                response = '상담에 대한 총평은 다음과 같다.\n'
                for summ in self.Expert[i]['counselling_summaries']:
                    response += summ['summary'] + "\n"
                    
                category = self.Expert[i]['job_label']
                Expert_summ = self.Expert[i]['expert_comment']['ko']
                response += f"추천 진로는 {category}이며, 이유는 다음과 같다. {Expert_summ}"
        
        return response
    
    def make_prompt(self, conv:str):
        prompt = f'아래는 작업 수행에 대한 지시문입니다. 상담 내용을 입력으로 사용해 응답을 완성해야 합니다.\n\n### 지시문:\n상담 내용을 가지고 요약 및 직업 추천을 합니다.\n\n### 상담 내용:\n{conv}\n\n### 응답:'
        return prompt
    
    def make_Data(self, idx:str):
        conv = self.get_Consultation_contents(idx)
        
        data = {'instruction':'상담 내용을 가지고 요약 및 직업 추천을 합니다.', 
            'input': conv, 
            'output':self.get_response(idx), 
            'prompt':self.make_prompt(conv)}
        
        return data
    
    

def main():
    with open("./Dataset/Training/Data/High/BasicInformation.json", "r") as f: #학생들 명단을 뽑아내기 위해서 사용됨
        HschoolBasicInfo = json.load(f)
    
    student_list = []
    for i in HschoolBasicInfo:
        student_list.append(HschoolBasicInfo[i]['meta_basics']['index'])
    
    cons_path = "./Dataset/Training/Data/High/ConsultationRecords.json"
    exp_path = "./Dataset/Training/LabeledData/LabeledHigh.json"

    customdata = CustomDatasetMaker(cons_path, exp_path, student_list)
    now = datetime.now()
    
    with open(f"./dataset_{now.year}_{now.month}_{now.day}_{now.time().second}.json", "w") as jsonfile:
        json.dump(customdata(), jsonfile)

    
if __name__ == "__main__":
    main()
