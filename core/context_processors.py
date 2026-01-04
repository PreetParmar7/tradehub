def profile_context(request):
    if request.user.is_authenticated:
        return {"profile": getattr(request.user, "profile", None)}
    return {"profile": None}
