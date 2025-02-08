from langgraph.types import Command

from graph.state import GraphState, GraphConfig


SYSTEM_PROMPT = """You are a movie recommendation expert who finds the best movies based on user preferences.

Your tasks:
1. Extract user preferences about movies from user requests.
2. Classify the extracted user preferences into one of two categories: whether they are related to given metadata or related to synopsis.
3. Find movies related to user preferences by using MovieRetrieverTool only once.
4. Based on the MovieRetrieverTool results, recommend movies that match the user's preferences.

METADATA:
- MovieID (TEXT): Unique identifier
- Title (TEXT): Movie title
- Year (FLOAT): Release year (0.0 if unknown)
- Genre (TEXT): Movie genre(s)
- Country (TEXT): Production country
- Runtime (TEXT): Duration (e.g. '1시간 30분')
- Age (TEXT): Rating ("전체"|"7세"|"12세"|"15세"|"청불")
- Cast_Production_Info_List (TEXT): Director and cast info as list of tuples
- Avg_Rating (FLOAT): Average rating 0-5
- N_Rating(만명) (FLOAT): Number of ratings in 10k
- N_Comments (FLOAT): Number of reviews

Example movie data:
| MovieID | Title | Year | Genre | Country | Runtime | Age | Cast & Production | Synopsis | Avg Rating | N_Rating(만명) | N_Comments |
|---------|--------|------|-------|----------|----------|-----|-----------------|-----------|------------|---------------|------------|
| m45nEnd | 사마리아 | 2004 | 드라마 | 한국 | 1시간 35분 | 청불 | 감독: 김기덕<br>주연: 이얼(영기), 곽지민 | "인도에 바수밀다 라는 창녀가 있었어. 그런데 그 창녀랑 잠만 자고 나면 남자들이..." | 2.8 | 3.45 | 0.0 |
| mWLjGNd | 택시 드라이버 | 1976 | 드라마 스릴러 | 미국 | 1시간 53분 | 청불 | 감독: 마틴 스콜세지<br>주연: 로버트 드 니로(트래비스) | 트래비스(로버트 드 니로)는 베트남전에서 귀환한 후 불면증에 시달리며 사회에 적응하... | 4.0 | 10.84 | 0.0 |
| mOk6BPQ | 파울볼 | 2014 | 다큐멘터리 | 한국 | 1시간 27분 | 전체 | 감독: 조정래, 김보경<br>나레이션: 조진웅 | 한,미,일 3개국 프로야구 선수 출신 최향남, 국내 프로야구 신인왕 출신 김수경 등... | 3.3 | 7355.0 | 50.0 |
| mdBzPGd | 청설 | 2009 | 드라마 로맨스 | 대만 | 1시간 49분 | 전체 | 감독: 청펀펀<br>주연: 펑위옌(티엔커), 진의함 | 손으로 말하는 '양양'과 그녀에게 첫눈에 반한 '티엔커'. 마음이 듣고 가슴으로 느... | 3.8 | 16.5 | 200.0 |
| mObJJRO | 하녀 라본느 | - | - | - | 1시간 22분 | 청불 | 감독: 살바토르 샘페리<br>주연: 플로랑스 구에린, 트린 | - | 2.5 | 36.0 | 10.0 |

Special notes:
- Missing values are marked as '-' or NULL
- Cast info format: [('감독명', '감독'), ('배우명', '주연 | 역할')]
"""


class RecommendMovieNode:
    def __init__(self, llm, tools):
        self.llm_with_tools = llm.bind_tools(tools)
        self.system_message = {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }

    def __call__(self, state: GraphState, config: GraphConfig) -> GraphState:
        messages = [self.system_message] + state.inter_messages
        result = self.llm_with_tools.invoke(messages)

        if result.tool_calls:
            if state.execute_tool_count >= config["configurable"]["max_execute_tool"]:
                return Command(
                    update={
                        "agent_results": [
                            f"Tool execution limit reached. Please try again later."
                        ],
                        "execute_tool_count": 0,
                    },
                    goto="supervisor_node",
                )
            else:
                return Command(
                    update={
                        "inter_messages": state.inter_messages + [result],
                    },
                    goto="execute_tool",
                )
        else:
            return Command(
                update={
                    "agent_results": [
                        f"<RecommendMovieAgent>\n{result.content}\n</RecommendMovieAgent>"
                    ],
                    "execute_tool_count": 0,
                },
                goto="supervisor_node",
            )