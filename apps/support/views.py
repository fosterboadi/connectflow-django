from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from apps.accounts.models import User
from .models import Ticket, TicketMessage
from .forms import TicketForm, TicketMessageForm, TicketAdminForm

def super_admin_check(user):
    return user.is_authenticated and user.role == User.Role.SUPER_ADMIN and user.is_staff

@login_required
def ticket_list(request):
    """List tickets for the current user."""
    tickets = Ticket.objects.filter(requester=request.user)
    return render(request, 'support/ticket_list.html', {'tickets': tickets})

@login_required
@user_passes_test(super_admin_check)
def platform_ticket_list(request):
    """List all tickets for platform admins."""
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    
    tickets = Ticket.objects.select_related('requester', 'organization', 'assigned_to').all()
    
    if query:
        tickets = tickets.filter(
            Q(subject__icontains=query) |
            Q(requester__username__icontains=query) |
            Q(organization__name__icontains=query)
        )
    
    if status_filter:
        tickets = tickets.filter(status=status_filter)
        
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
        
    return render(request, 'support/platform/ticket_list.html', {
        'tickets': tickets,
        'search_query': query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'statuses': Ticket.Status.choices,
        'priorities': Ticket.Priority.choices
    })

@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        message_form = TicketMessageForm(request.POST, request.FILES)
        
        if form.is_valid() and message_form.is_valid():
            ticket = form.save(commit=False)
            ticket.requester = request.user
            ticket.save() # This triggers the priority auto-detection in save() logic
            
            # Create initial message
            message = message_form.save(commit=False)
            message.ticket = ticket
            message.sender = request.user
            message.save()
            
            messages.success(request, "Support ticket created successfully.")
            return redirect('support:ticket_detail', pk=ticket.pk)
    else:
        form = TicketForm()
        message_form = TicketMessageForm()
    
    return render(request, 'support/ticket_create.html', {
        'form': form,
        'message_form': message_form
    })

@login_required
def chatbot(request):
    """Render the AI Chatbot interface."""
    return render(request, 'support/chatbot.html')

@login_required
@user_passes_test(super_admin_check)
def platform_ticket_detail(request, pk):
    """Detail view for platform admins to manage a ticket."""
    ticket = get_object_or_404(Ticket, pk=pk)
    
    if request.method == 'POST':
        if 'update_ticket' in request.POST:
            admin_form = TicketAdminForm(request.POST, instance=ticket)
            if admin_form.is_valid():
                admin_form.save()
                messages.success(request, "Ticket details updated.")
                return redirect('support:platform_ticket_detail', pk=pk)
        
        elif 'send_message' in request.POST:
            message_form = TicketMessageForm(request.POST, request.FILES)
            if message_form.is_valid():
                message = message_form.save(commit=False)
                message.ticket = ticket
                message.sender = request.user
                message.is_internal_note = request.POST.get('is_internal_note') == 'on'
                message.save()
                
                # If not an internal note, update status to AWAITING_USER
                if not message.is_internal_note:
                    ticket.status = Ticket.Status.AWAITING_USER
                    ticket.save()
                
                messages.success(request, "Message sent.")
                return redirect('support:platform_ticket_detail', pk=pk)
    else:
        admin_form = TicketAdminForm(instance=ticket)
        message_form = TicketMessageForm()
        
    messages_list = ticket.messages.all()
    
    return render(request, 'support/platform/ticket_detail.html', {
        'ticket': ticket,
        'messages': messages_list,
        'admin_form': admin_form,
        'message_form': message_form
    })

@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Access control: requester or admin
    if ticket.requester != request.user and not request.user.is_admin:
        messages.error(request, "You do not have permission to view this ticket.")
        return redirect('support:ticket_list')
    
    if request.method == 'POST':
        form = TicketMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.ticket = ticket
            message.sender = request.user
            message.save()
            
            # Update ticket status if needed (e.g., if user replies, move from AWAITING_USER to OPEN)
            if request.user == ticket.requester and ticket.status == Ticket.Status.AWAITING_USER:
                ticket.status = Ticket.Status.IN_PROGRESS
                ticket.save()
                
            messages.success(request, "Reply sent.")
            return redirect('support:ticket_detail', pk=pk)
    else:
        form = TicketMessageForm()
        
    # Users should not see internal notes
    messages_list = ticket.messages.filter(is_internal_note=False)
    
    return render(request, 'support/ticket_detail.html', {
        'ticket': ticket,
        'messages': messages_list,
        'form': form
    })
