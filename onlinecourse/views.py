
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Exam, Submission


def course_details(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(
        request,
        "course_details_bootstrap.html",
        {"course": course},
    )


@login_required
def submit(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.method == "POST":
        score = 0
        questions = exam.questions.prefetch_related("choices")

        for question in questions:
            selected_id = request.POST.get(f"question_{question.id}")
            if selected_id:
                choice = question.choices.filter(id=selected_id).first()
                if choice and choice.is_correct:
                    score += 1

        submission = Submission.objects.create(
            user=request.user,
            exam=exam,
            score=score,
        )
        return redirect("show_exam_result", submission_id=submission.id)

    return render(request, "exam.html", {"exam": exam})


@login_required
def show_exam_result(request, submission_id):
    submission = get_object_or_404(
        Submission.objects.select_related("user", "exam"),
        id=submission_id,
        user=request.user,
    )

    total_questions = submission.exam.questions.count()

    return render(
        request,
        "exam_result.html",
        {
            "submission": submission,
            "total_questions": total_questions,
        },
    )
