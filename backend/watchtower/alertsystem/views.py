from rest_framework.decorators import api_view
from rest_framework.response import Response
import ollama

@api_view(['POST'])
def get_explanation(request):
    prediction = request.data.get('prediction')
    if not prediction:
        return Response({"error": "No prediction provided"}, status=400)

    try:
        response = ollama.chat(model='llama2', messages=[
            {'role': 'user', 'content': prediction},
        ])
        explanation = response['message']['content']
    except ollama.ResponseError as e:
        return Response({"error": f"Failed to get explanation from Ollama: {str(e)}"}, status=500)
    
    return Response({'explanation': explanation})
