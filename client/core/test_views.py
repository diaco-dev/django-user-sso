# views.py - Add these views to test your DRF API with OAuth

import requests
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import logging

from task.models import Task
from task.serializers import TaskSerializer

logger = logging.getLogger(__name__)


def test_api_dashboard(request):
    """Dashboard to test various API endpoints"""
    if 'user' not in request.session:
        return HttpResponse("Please login first: <a href='/login/'>Login</a>", status=401)

    access_token = request.session.get('access_token')
    user_info = request.session.get('user')

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Test Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 20px auto; padding: 20px; }}
            .user-info {{ background: #f0f0f0; padding: 15px; margin-bottom: 20px; border-radius: 5px; }}
            .test-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            button {{ padding: 10px 15px; margin: 5px; background: #007cba; color: white; border: none; cursor: pointer; border-radius: 3px; }}
            button:hover {{ background: #005a87; }}
            .result {{ background: #f9f9f9; padding: 10px; margin-top: 10px; border-radius: 3px; white-space: pre-wrap; }}
            input[type="text"] {{ padding: 8px; margin: 5px; width: 200px; }}
        </style>
        <script>
            async function testAPI(endpoint, method = 'GET', data = null) {{
                const token = '{access_token}';
                const url = 'http://localhost:8001' + endpoint;

                const options = {{
                    method: method,
                    headers: {{
                        'Authorization': 'Bearer ' + token,
                        'Content-Type': 'application/json',
                    }}
                }};

                if (data && method !== 'GET') {{
                    options.body = JSON.stringify(data);
                }}

                try {{
                    const response = await fetch(url, options);
                    const result = await response.json();

                    document.getElementById('result').textContent = 
                        `Status: ${{response.status}}\\n` +
                        `Response: ${{JSON.stringify(result, null, 2)}}`;
                }} catch (error) {{
                    document.getElementById('result').textContent = 
                        `Error: ${{error.message}}`;
                }}
            }}

            function createTask() {{
                const title = document.getElementById('task-title').value;
                if (!title) {{
                    alert('Please enter a task title');
                    return;
                }}

                const taskData = {{
                    title: title,
                    description: 'Created via OAuth API test',
                    status: 'pending'
                }};

                testAPI('/api/v1/task/task/', 'POST', taskData);
            }}
        </script>
    </head>
    <body>
        <h1>🚀 API Test Dashboard</h1>

        <div class="user-info">
            <h3>👤 Logged in as: {user_info.get('username', 'Unknown')}</h3>
            <p><strong>Email:</strong> {user_info.get('email', 'N/A')}</p>
            <p><strong>Access Token:</strong>{access_token if access_token else 'None'}</p>
        </div>

        <div class="test-section">
            <h3>📋 Task API Tests</h3>
            <button onclick="testAPI('/api/v1/task/task/')">GET All Tasks</button>
            <button onclick="testAPI('/api/v1/task/task/1/')">GET Task #1</button>
            <button onclick="testAPI('/api/v1/task/task/?search=test')">Search Tasks</button>
            <br>
            <input type="text" id="task-title" placeholder="New task title">
            <button onclick="createTask()">Create Task</button>
            <button onclick="testAPI('/api/v1/task/task/1/', 'DELETE')">Delete Task #1</button>
        </div>

        <div class="test-section">
            <h3>🔐 Auth Tests</h3>
            <button onclick="testAPI('/api/user-info/')">Get User Info</button>
            <button onclick="testAPI('/api/protected-test/')">Test Protected Endpoint</button>
        </div>

        <div class="test-section">
            <h3>📊 Response:</h3>
            <div id="result" class="result">Click a button above to test the API...</div>
        </div>

        <div class="test-section">
            <h3>🔗 Direct Links</h3>
            <a href="/logout/" style="color: red;">Logout</a> | 
            <a href="/api/v1/task/task/" target="_blank">Open API in new tab</a>
        </div>
    </body>
    </html>
    """

    return HttpResponse(html_content)


@csrf_exempt
def test_api_endpoint(request):
    """Server-side API testing endpoint"""
    if 'access_token' not in request.session:
        return JsonResponse({'error': 'No access token available'}, status=401)

    access_token = request.session['access_token']

    # Test different API endpoints
    test_results = {}

    # Test 1: Get all tasks
    try:
        response = requests.get(
            'http://localhost:8001/api/v1/task/task/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        test_results['get_tasks'] = {
            'status': response.status_code,
            'data': response.json() if response.headers.get('content-type', '').startswith(
                'application/json') else response.text
        }
    except Exception as e:
        test_results['get_tasks'] = {'error': str(e)}

    # Test 2: Create a task
    try:
        task_data = {
            'title': 'OAuth Test Task',
            'description': 'Created via OAuth authentication',
            'status': 'pending'
        }
        response = requests.post(
            'http://localhost:8001/api/v1/task/task/',
            json=task_data,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        test_results['create_task'] = {
            'status': response.status_code,
            'data': response.json() if response.headers.get('content-type', '').startswith(
                'application/json') else response.text
        }
    except Exception as e:
        test_results['create_task'] = {'error': str(e)}

    # Test 3: Search tasks
    try:
        response = requests.get(
            'http://localhost:8001/api/v1/task/task/?search=OAuth',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        test_results['search_tasks'] = {
            'status': response.status_code,
            'data': response.json() if response.headers.get('content-type', '').startswith(
                'application/json') else response.text
        }
    except Exception as e:
        test_results['search_tasks'] = {'error': str(e)}

    return JsonResponse(test_results)









def test_session(request):
    """Test session functionality"""
    # Set a test value
    request.session['test_key'] = 'test_value'
    request.session.save()

    return JsonResponse({
        'session_key': request.session.session_key,
        'test_value': request.session.get('test_key'),
        'session_items': dict(request.session),
        'cookies': dict(request.COOKIES),
    })
