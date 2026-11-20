from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Choice, Question
from django.http import HttpResponse
from django.utils.html import escape


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

# @login_required  <--- FIX BROKEN ACCESS CONTROL
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    # BROKEN ACCESS CONTROL Flaw
    # ---------------------------------------
    login_status = request.POST.get('user_logged_in', 'false')  # <-- Comment this out

    if login_status != 'true': # <-- Comment this out
        return HttpResponse("Error: Only users that are logged in can vote!") # <-- Comment this out
    # ---------------------------------------
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

def search(request):
    query = request.GET.get("q", "").strip()

    form_html = f"""
    <form method="get" action="">
        <label for="q">Search Questions:</label>
        <input type="text" id="q" name="q" value="{escape(query)}" placeholder="Search">
        <button type="submit">Search</button>
        </form>
        <hr>
        """


    if query:
        # <---------- Injection FLAW
        sql = f"SELECT * FROM polls_question WHERE question_text LIKE '%{query}%'"
        questions = list(Question.objects.raw(sql))
        # -------------------------- ' UNION SELECT id, secret_token, NULL, NULL, NULL FROM polls_question --
        
        # ------------ Injection FIX
        # sql = "SELECT * FROM polls_question WHERE question_text LIKE %s"
        # questions = list(Question.objects.raw(sql, [f"%{query}%"]))
        # -----------------------------------------------------------------
        heading = "<h2>Search results:</h2>"
    else:
        questions = list(Question.objects.order_by("-pub_date")[:5])
        heading = "<h2> Latest questions:</h2>"

    if questions:
        items = "".join(f'<li><a href="{reverse("polls:detail", args=(q.id,))}">{escape(q.question_text)}</a></li>' for q in questions )

        list_html = f"<ul>{items}</ul>"
    else:
        list_html = "<p>Questions not found</p>"

    return HttpResponse(form_html + heading + list_html)
    
