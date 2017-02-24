from django.shortcuts import render

# Create your views here.

def account(request):
    context = {
    }
    if request.method=='POST':
        form = loginForm(request.POST)
    else:
        print("nope")

    return render(request, 'account/myAccount.html', context)