import json
import os
import re
import numpy as np
import requests

# Global model configuration cache
_model_config = None

def get_model(model_key: str) -> str:
    """直接从JSON读取模型名称"""
    global _model_config
    if _model_config is None:
        config_path = os.path.join(os.path.dirname(__file__), 'model_config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                _model_config = json.load(f)
        except:
            _model_config = {}
    
    return _model_config.get(model_key, 'gpt-4o-mini')

class JSONExtractError(Exception):
    def __init__(self, ErrorInfo):
        super().__init__(self)
        self.errorinfo=ErrorInfo
    def __str__(self):
        return self.errorinfo

def ask_openai_common(prompt):
        api_base = os.environ.get('OPENAI_API_BASE', 'api.openai.com')  # Replace with your actual OpenAI API base URL
        api_key = os.environ.get('OPENAI_API_KEY')  # Replace with your actual OpenAI API key
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "model": get_model('openai_general'),  # Obtain OpenAI model via the model manager
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        response = requests.post(f'https://{api_base}/v1/chat/completions', headers=headers, json=data)
        try:
            response_josn = response.json()
        except Exception as e:
            return ''
        if 'choices' not in response_josn:
            return ''
        return response_josn['choices'][0]['message']['content']
def ask_openai_for_json(prompt):
    api_base = os.environ.get('OPENAI_API_BASE', 'api.openai.com')  # Replace with your actual OpenAI API base URL
    api_key = os.environ.get('OPENAI_API_KEY')  # Replace with your actual OpenAI API key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": get_model('structured_json_extraction'),
        "response_format": { "type": "json_object" },
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant designed to output JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    # response = requests.post(f'https://{api_base}/v1/chat/completions', headers=headers, json=data)
    # # if response.status_code != 200:
    # #     print(response.text)
    
    # response_josn = response.json()
    # if 'choices' not in response_josn:
    #     return ''
    # # print(response_josn['choices'][0]['message']['content'])
    # return response_josn['choices'][0]['message']['content']
    while True:
        try:
            response = requests.post(f'https://{api_base}/v1/chat/completions', headers=headers, json=data)
            response_json = response.json()
            if 'choices' not in response_json:
                return ''
            response_content = response_json['choices'][0]['message']['content']
            if "```json" in response_content:
                try:
                    cleaned_json = extract_json_string(response_content)
                    break
                except JSONExtractError as e:
                    print(e)
                    print("===Error in extracting json. Retry request===")
                    continue
            else:
                try:
                    decoded_content = json.loads(response_content)
                    if isinstance(decoded_content, dict):
                        cleaned_json = response_content
                        break
                    else:
                        print("===Unexpected JSON format. Retry request===")
                        print(response_content)
                        continue
                except json.JSONDecodeError as e:
                    print("===Error in decoding JSON. Retry request===")
                    continue
                except Exception as e:
                    print("===Unexpected error. Retry request===")
                    print(e)
                    continue
        except Exception as e:
            print("===Error in requesting LLM. Retry request===")
    return cleaned_json

def extract_json_string(response):
    json_pattern = re.compile(r'```json(.*?)```', re.DOTALL)
    response = response.strip()
    extracted_json = re.findall(json_pattern, response)
    if len(extracted_json) > 1:
        print("[DEBUG]⚠️Error json string:")
        print(response)
        raise JSONExtractError("⚠️Return JSON format error: More than one JSON format found")
    elif len(extracted_json) == 0:
        print("[DEBUG]⚠️Error json string:")
        print(response)
        raise JSONExtractError("⚠️Return JSON format error: No JSON format found")
    else:
        cleaned_json = extracted_json[0]
        data_json = json.loads(cleaned_json)
        if isinstance(data_json, dict):
            return cleaned_json
        else:
            print("[DEBUG]⚠️Error json string:")
            print(response)
            raise JSONExtractError("⚠️Return JSON format error: input format is not a JSON")

def extract_structured_json(prompt):
    return ask_openai_for_json(prompt)
def detect_vulnerabilities(prompt):
    model = get_model('vulnerability_detection')
    api_key = os.environ.get('OPENAI_API_KEY')
    api_base = os.environ.get('OPENAI_API_BASE')
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
        'model': model,
        'messages': [
            {
                'role': 'user',
                'content': prompt
            }
        ]
    }

    try:
        response = requests.post(f'https://{api_base}/v1/chat/completions', 
                               headers=headers, 
                               json=data)
        response.raise_for_status()
        response_data = response.json()
        if 'choices' in response_data and len(response_data['choices']) > 0:
            return response_data['choices'][0]['message']['content']
        else:
            return ""
    except requests.exceptions.RequestException as e:
        print(f"Vulnerability API call failed. Error: {str(e)}")
        return ""
def analyze_code_assumptions(prompt):
    model = get_model('code_assumptions_analysis')
    api_key = os.environ.get('OPENAI_API_KEY','sk-0fzQWrcTc0DASaFT7Q0V0e7c24ZyHMKYgIDpXWrry8XHQAcj')
    api_base = os.environ.get('OPENAI_API_BASE', '4.0.wokaai.com')
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
        'model': model,
        'messages': [
            {
                'role': 'user',
                'content': prompt
            }
        ]
    }

    try:
        response = requests.post(f'https://{api_base}/v1/chat/completions', 
                               headers=headers, 
                               json=data)
        response.raise_for_status()
        response_data = response.json()
        if 'choices' in response_data and len(response_data['choices']) > 0:
            return response_data['choices'][0]['message']['content']
        else:
            return ""
    except requests.exceptions.RequestException as e:
        print(f"Claude API call failed. Error: {str(e)}")
        return ""

def ask_deepseek(prompt):
    model = 'deepseek-reasoner'
    # print("prompt:",prompt)
    api_key = os.environ.get('OPENAI_API_KEY')
    api_base = os.environ.get('OPENAI_API_BASE', '4.0.wokaai.com')
    # print("api_base:",api_base)
    # print("api_key:",api_key)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
        'model': model,
        'messages': [
            {
                'role': 'user',
                'content': prompt
            }
        ]
    }

    try:
        response = requests.post(f'https://{api_base}/v1/chat/completions', 
                               headers=headers, 
                               json=data)
        response.raise_for_status()
        response_data = response.json()
        if 'choices' in response_data and len(response_data['choices']) > 0:
            return response_data['choices'][0]['message']['content']
        else:
            return ""
    except requests.exceptions.RequestException as e:
        print(f"wokaai deepseek API call failed. Error: {str(e)}")
        return ""








def clean_text(text: str) -> str:
    return str(text).replace(" ", "").replace("\n", "").replace("\r", "")

def common_get_embedding(text: str):
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    api_base = os.getenv('OPENAI_API_BASE', 'api.openai.com')
    model = get_model("embedding_model")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    cleaned_text = clean_text(text)
    
    data = {
        "input": cleaned_text,
        "model": model,
        "encoding_format": "float"
    }

    try:
        response = requests.post(f'https://{api_base}/v1/embeddings', json=data, headers=headers)
        response.raise_for_status()
        embedding_data = response.json()
        return embedding_data['data'][0]['embedding']
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return list(np.zeros(3072))  # Return an all-zero array of length 3072


# ========== Multi-round vulnerability analysis specialized functions ==========

def perform_initial_vulnerability_validation(prompt):
    """
    Agent initial analysis - perform preliminary vulnerability detection analysis
    Env vars: AGENT_INITIAL_MODEL (default: claude-3-haiku-20240307)
    """
    model = get_model('initial_vulnerability_validation')
    api_key = os.environ.get('OPENAI_API_KEY')
    api_base = os.environ.get('OPENAI_API_BASE', '4.0.wokaai.com')
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
        'model': model,
        'messages': [
            {
                'role': 'user',
                'content': prompt
            }
        ]
    }

    try:
        response = requests.post(f'https://{api_base}/v1/chat/completions', 
                               headers=headers, 
                               json=data)
        response.raise_for_status()
        response_data = response.json()
        if 'choices' in response_data and len(response_data['choices']) > 0:
            return response_data['choices'][0]['message']['content']
        else:
            return ""
    except requests.exceptions.RequestException as e:
        print(f"Agent initial analysis API call failed. Error: {str(e)}")
        return ""


def extract_vulnerability_findings_json(prompt):
    """
    Agent JSON extraction - extract structured JSON from natural language
    Env vars: AGENT_JSON_MODEL (default: gpt-4o-mini)
    """
    model = get_model('vulnerability_findings_json_extraction')
    api_key = os.environ.get('OPENAI_API_KEY')
    api_base = os.environ.get('OPENAI_API_BASE', '4.0.wokaai.com')
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
        'model': model,
        'messages': [
            {
                'role': 'user',
                'content': prompt
            }
        ]
    }

    try:
        response = requests.post(f'https://{api_base}/v1/chat/completions', 
                               headers=headers, 
                               json=data)
        response.raise_for_status()
        response_data = response.json()
        if 'choices' in response_data and len(response_data['choices']) > 0:
            return response_data['choices'][0]['message']['content']
        else:
            return ""
    except requests.exceptions.RequestException as e:
        print(f"Agent JSON extraction API call failed. Error: {str(e)}")
        return ""


def determine_additional_context_needed(prompt):
    """
    Agent info query - determine what additional information is needed
    Env vars: AGENT_INFO_QUERY_MODEL (default: claude-3-sonnet-20240229)
    """
    model = get_model('additional_context_determination')
    api_key = os.environ.get('OPENAI_API_KEY')
    api_base = os.environ.get('OPENAI_API_BASE', '4.0.wokaai.com')
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
        'model': model,
        'messages': [
            {
                'role': 'user',
                'content': prompt
            }
        ]
    }

    try:
        response = requests.post(f'https://{api_base}/v1/chat/completions', 
                               headers=headers, 
                               json=data)
        response.raise_for_status()
        response_data = response.json()
        if 'choices' in response_data and len(response_data['choices']) > 0:
            return response_data['choices'][0]['message']['content']
        else:
            return ""
    except requests.exceptions.RequestException as e:
        print(f"Agent info query API call failed. Error: {str(e)}")
        return ""




def perform_comprehensive_vulnerability_analysis(prompt):
    """
    Agent final analysis - make the final judgment based on all collected information
    Env vars: AGENT_FINAL_MODEL (default: claude-opus-4-20250514)
    """
    model = get_model('comprehensive_vulnerability_analysis')
    api_key = os.environ.get('OPENAI_API_KEY')
    api_base = os.environ.get('OPENAI_API_BASE', '4.0.wokaai.com')
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    data = {
        'model': model,
        'messages': [
            {
                'role': 'user',
                'content': prompt
            }
        ]
    }

    try:
        response = requests.post(f'https://{api_base}/v1/chat/completions', 
                               headers=headers, 
                               json=data)
        response.raise_for_status()
        response_data = response.json()
        if 'choices' in response_data and len(response_data['choices']) > 0:
            return response_data['choices'][0]['message']['content']
        else:
            return ""
    except requests.exceptions.RequestException as e:
        print(f"Agent final analysis API call failed. Error: {str(e)}")
        return ""


def summarize_group_vulnerability_results(group_results_prompt: str) -> str:
    """Summarize vulnerability results of a group of tasks using an LLM
    
    Args:
        group_results_prompt: Full prompt containing the grouped results
        
    Returns:
        str: LLM-generated vulnerability summary
    """
    try:
        # 从model_config.json获取用于总结的模型配置
        # 使用专门的group_results_summarization模型进行总结
        model_key = "group_results_summarization"
        
        # 构建API请求
        payload = {
            "model": get_model_by_key(model_key),
            "messages": [
                {
                    "role": "user", 
                    "content": group_results_prompt
                }
            ],
            "temperature": 0.3,  # Lower temperature ensures consistency in summarization
            "max_tokens": 1000   # Limit summary length
        }
        
        print(f"🤖 Using model {get_model_by_key(model_key)} to summarize grouped vulnerability results...")
        
        response = requests.post(
            get_api_url(),
            json=payload,
            headers=get_headers(),
            proxies=get_proxies()
        )
        
        response_data = response.json()
        
        if 'choices' in response_data and len(response_data['choices']) > 0:
            summary = response_data['choices'][0]['message']['content']
            print(f"✅ Group results summary completed, length: {len(summary)} chars")
            return summary
        else:
            print("⚠️ Group results summary API response format unexpected")
            return ""
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Group results summary API call failed: {str(e)}")
        return ""
    except Exception as e:
        print(f"❌ Group results summary processing failed: {str(e)}")
        return ""



