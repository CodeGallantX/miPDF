import io
import os
from django.contrib.auth.models import User
from django.http import FileResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import fitz  # PyMuPDF
import PyPDF2
from pdf2docx import Converter
from .models import PDFHistory  # Ensure this model exists

# ========================
# 🔐 Authentication Views
# ========================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user with username and password"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return JsonResponse({'error': 'Both username and password are required'}, status=400)
        
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Username already exists'}, status=400)
        
    User.objects.create_user(username=username, password=password)
    return JsonResponse({'message': 'User registered successfully'}, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login user and return JWT tokens"""
    username = request.data.get('username')
    password = request.data.get('password')
    user = User.objects.filter(username=username).first()
    
    if not user or not user.check_password(password):
        return JsonResponse({'error': 'Invalid credentials'}, status=401)
        
    refresh = RefreshToken.for_user(user)
    return JsonResponse({
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    })

# ========================
# 📄 PDF Operations Views
# ========================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def text_to_pdf(request):
    """Convert text to styled PDF with history tracking"""
    text = request.data.get('text', '')
    if not text:
        return JsonResponse({'error': 'Text is required'}, status=400)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    
    # Improved text formatting
    text_obj = pdf.beginText(40, 750)  # x, y coordinates
    text_obj.setFont("Helvetica", 12)
    text_obj.textLines(text)  # Handles multi-line text
    pdf.drawText(text_obj)
    pdf.save()
    
    buffer.seek(0)
    
    # Save to history
    PDFHistory.objects.create(
        user=request.user,
        file_name="text_to_pdf.pdf",
        action="TEXT_TO_PDF"
    )
    
    return FileResponse(buffer, as_attachment=True, filename="converted.pdf")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def merge_pdfs(request):
    """Merge multiple PDFs into one"""
    pdf_files = request.FILES.getlist('pdfs')
    if len(pdf_files) < 2:
        return JsonResponse({'error': 'At least 2 PDFs required'}, status=400)

    merger = PyPDF2.PdfMerger()
    
    try:
        for pdf in pdf_files:
            merger.append(pdf)
            
        buffer = io.BytesIO()
        merger.write(buffer)
        buffer.seek(0)
        
        # Save to history
        PDFHistory.objects.create(
            user=request.user,
            file_name="merged.pdf",
            action="MERGE_PDFS"
        )
        
        return FileResponse(buffer, as_attachment=True, filename="merged.pdf")
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        merger.close()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pdf_to_word(request):
    """Convert PDF to Word document"""
    pdf_file = request.FILES.get('pdf')
    if not pdf_file:
        return JsonResponse({'error': 'PDF file is required'}, status=400)

    try:
        # Use in-memory files to avoid disk I/O
        pdf_buffer = io.BytesIO(pdf_file.read())
        word_buffer = io.BytesIO()
        
        cv = Converter(pdf_buffer)
        cv.convert(word_buffer)
        cv.close()
        
        word_buffer.seek(0)
        
        # Save to history
        PDFHistory.objects.create(
            user=request.user,
            file_name="converted.docx",
            action="PDF_TO_WORD"
        )
        
        return FileResponse(word_buffer, as_attachment=True, filename="converted.docx")
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def highlight_pdf(request):
    """Highlight text in a PDF"""
    pdf_file = request.FILES.get('pdf')
    text = request.data.get('text', '')
    
    if not pdf_file:
        return JsonResponse({'error': 'PDF file is required'}, status=400)
    if not text:
        return JsonResponse({'error': 'Text to highlight is required'}, status=400)

    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        for page in doc:
            matches = page.search_for(text)
            for rect in matches:
                page.add_highlight_annot(rect)
                
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        # Save to history
        PDFHistory.objects.create(
            user=request.user,
            file_name="highlighted.pdf",
            action="HIGHLIGHT_PDF"
        )
        
        return FileResponse(buffer, as_attachment=True, filename="highlighted.pdf")
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        if 'doc' in locals():
            doc.close()

# ========================
# 📜 History Views
# ========================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_history(request):
    """Get user's PDF conversion history"""
    history = PDFHistory.objects.filter(user=request.user).order_by('-created_at')
    return JsonResponse({
        'history': [
            {
                'action': item.action,
                'file_name': item.file_name,
                'timestamp': item.created_at
            }
            for item in history
        ]
    })