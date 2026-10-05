from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from .models import Folder, Document, DocumentVersion
from .forms import FolderForm, DocumentUploadForm, DocumentVersionForm
import os

@login_required
def document_list(request, folder_id=None):
    """View documents and folders"""
    org = request.user.organization
    
    current_folder = None
    if folder_id:
        current_folder = get_object_or_404(Folder, id=folder_id, organization=org)
        folders = current_folder.subfolders.all()
        documents = current_folder.documents.all()
    else:
        folders = Folder.objects.filter(organization=org, parent=None)
        documents = Document.objects.filter(organization=org, folder=None)
        
    context = {
        'current_folder': current_folder,
        'folders': folders,
        'documents': documents,
        'breadcrumbs': _get_breadcrumbs(current_folder),
    }
    return render(request, 'tools/documents/index.html', context)

def _get_breadcrumbs(folder):
    breadcrumbs = []
    curr = folder
    while curr:
        breadcrumbs.insert(0, curr)
        curr = curr.parent
    return breadcrumbs

@login_required
def folder_create(request, parent_id=None):
    """Create a new folder"""
    parent = None
    if parent_id:
        parent = get_object_or_404(Folder, id=parent_id, organization=request.user.organization)
        
    if request.method == 'POST':
        form = FolderForm(request.POST)
        form.fields['parent'].queryset = Folder.objects.filter(
            organization=request.user.organization
        )
        if form.is_valid():
            folder = form.save(commit=False)
            folder.organization = request.user.organization
            folder.created_by = request.user
            if parent:
                folder.parent = parent
            folder.save()
            messages.success(request, f"Folder '{folder.name}' created.")
            return redirect('tools:documents:index_with_folder', folder_id=folder.id) if folder.parent else redirect('tools:documents:index')
    else:
        form = FolderForm(initial={'parent': parent})
        form.fields['parent'].queryset = Folder.objects.filter(
            organization=request.user.organization
        )
        
    return render(request, 'tools/documents/folder_form.html', {'form': form, 'title': 'Create Folder'})

@login_required
def document_upload(request, folder_id=None):
    """Upload a new document"""
    folder = None
    if folder_id:
        folder = get_object_or_404(Folder, id=folder_id, organization=request.user.organization)
        
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.organization = request.user.organization
            document.created_by = request.user
            if folder:
                document.folder = folder
            document.save()
            
            # Create the first version
            version = DocumentVersion.objects.create(
                document=document,
                file=request.FILES['file'],
                change_log=request.POST.get('change_log', 'Initial upload'),
                created_by=request.user
            )
            
            document.current_version = version
            document.save()
            
            messages.success(request, f"Document '{document.title}' uploaded.")
            return redirect('tools:documents:index_with_folder', folder_id=folder.id) if folder else redirect('tools:documents:index')
    else:
        form = DocumentUploadForm(initial={'folder': folder})
        form.fields['folder'].queryset = Folder.objects.filter(
            organization=request.user.organization
        )
        
    return render(request, 'tools/documents/upload_form.html', {'form': form, 'title': 'Upload Document'})

@login_required
def document_download(request, pk):
    """Download the current version of a document"""
    document = get_object_or_404(Document, pk=pk, organization=request.user.organization)
    if not document.current_version:
        messages.error(request, "This document has no files.")
        return redirect('tools:documents:index')
        
    version = document.current_version
    response = FileResponse(version.file.open(), content_type=version.file_type)
    response['Content-Disposition'] = f'attachment; filename="{version.file_name}"'
    return response

@login_required
def document_delete(request, pk):
    """Delete a document"""
    document = get_object_or_404(Document, pk=pk, organization=request.user.organization)
    title = document.title
    folder_id = document.folder.id if document.folder else None
    document.delete()
    messages.success(request, f"Document '{title}' deleted.")
    return redirect('tools:documents:index_with_folder', folder_id=folder_id) if folder_id else redirect('tools:documents:index')