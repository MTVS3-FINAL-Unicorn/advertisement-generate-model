import pyLDAvis
import pyLDAvis.lda_model
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.model_selection import GridSearchCV
import json

class TopicModel():
    def __init__(self, token_list, corp_id, meeting_id):
        self.count_vec = CountVectorizer(max_df=10, max_features=1000, min_df=1, ngram_range=(1,2))
        self.feat_vec = self.count_vec.fit_transform(token_list)
        self.lda = LatentDirichletAllocation(random_state=42)
        self.param_grid = {'n_components': [3, 4, 5]}
        self.search = GridSearchCV(self.lda, self.param_grid, cv=3)
        self.search.fit(self.feat_vec)
        self.best_model = self.search.best_estimator_
        self.feature_names = self.count_vec.get_feature_names_out()
        
        self.meeting_id = meeting_id
        self.corp_id = corp_id

    def show_topics(self, num_top_words):
        for topic_idx, topic in enumerate(self.best_model.components_):
            print(f'Topic {topic_idx+1}')
            
            topic_word_idx = topic.argsort()[::-1]
            top_idx = topic_word_idx[:num_top_words]
            
            result_text = ' '.join([self.feature_names[i] for i in top_idx])
            print(result_text)
    
    def make_analyze_result(self):
        try:
            # Prepare the visualization data
            vis = pyLDAvis.lda_model.prepare(self.best_model, self.feat_vec, self.count_vec)
            vis_file = f'{self.meeting_id}.html'
            pyLDAvis.save_html(vis, './'+vis_file)
            return vis_file
        except Exception as e:
            print(f"An error occurred while creating the visualization: {str(e)}")
    
    def prepared_data_to_json(self, prepared_data):
        # 변환된 JSON 데이터 생성
        json_data = {
            "mdsDat": {
                "x": prepared_data.topic_coordinates['x'].tolist(),
                "y": prepared_data.topic_coordinates['y'].tolist(),
                "topics": prepared_data.topic_coordinates['topics'].tolist(),
                "cluster": prepared_data.topic_coordinates['cluster'].tolist(),
                "Freq": prepared_data.topic_coordinates['Freq'].tolist(),
            },
            "tinfo": {
                "Term": prepared_data.topic_info['Term'].tolist(),
                "Freq": prepared_data.topic_info['Freq'].tolist(),
                "Total": prepared_data.topic_info['Total'].tolist(),
                "Category": prepared_data.topic_info['Category'].tolist(),
                "logprob": prepared_data.topic_info['logprob'].tolist(),
                "loglift": prepared_data.topic_info['loglift'].tolist(),
            },
            "token.table": {
                "Topic": prepared_data.token_table['Topic'].tolist(),
                "Freq": prepared_data.token_table['Freq'].tolist(),
                "Term": prepared_data.token_table['Term'].tolist(),
            },
            "R": prepared_data.R,
            "lambda.step": prepared_data.lambda_step,
            "plot.opts": prepared_data.plot_opts,
            "topic.order": prepared_data.topic_order
        }
        
        return json.dumps(json_data)

    def make_lda_json(self):
        vis_data = pyLDAvis.lda_model.prepare(self.best_model, self.feat_vec, self.count_vec)
        json_data = self.prepared_data_to_json(vis_data)
        print(json_data)
        return json_data

if __name__ == '__main__':
    token_list = ['매운', '음식', '정말', '좋아해요', '떡볶이', '자주', '매콤', '달콤한', '양념', '입안', '쫄깃', '매일', '질리', '음식', '하나', '입니다', '때로는', '라면', '사리', '먹기', '어묵', '계란', '추가', '더욱', '성한', '있어요', '분식집', '즉석', '떡볶이', '더욱', '특별하죠', '매운', '좋아하는', '사람', '떡볶이', '정말', '최고', '음식', '파스타', '정말', '좋아해요', '파스타', '여러', '종류']
    topic_model = TopicModel(token_list, 0, 0)
    # topic_model.make_analyze_result()
    topic_model.make_lda_json()