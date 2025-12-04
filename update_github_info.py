"""
Script para actualizar la descripción del repositorio en GitHub usando la API.

Requiere: pip install requests
"""
import requests
import os

# Configuración
GITHUB_TOKEN = "ghp_kHNfNJLbWOKJnpNjPIrZKNpnwBhXKD0zzEQI"
REPO_OWNER = "elvis3770"
REPO_NAME = "WebAI-to-API-master"

# Nueva descripción y configuración
NEW_DESCRIPTION = "🚀 Production-ready FastAPI wrapper for Gemini with AI agent support. Features: chaining, model routing, token tracking, LangChain/CrewAI/AutoGen integration. 22% faster than original."
NEW_HOMEPAGE = "https://github.com/elvis3770/WebAI-to-API-master"
TOPICS = ["ai", "agents", "gemini", "fastapi", "langchain", "crewai", "autogen", "llm", "api", "python"]

def update_repo_info():
    """Actualiza la información del repositorio."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "description": NEW_DESCRIPTION,
        "homepage": NEW_HOMEPAGE,
        "has_issues": True,
        "has_projects": True,
        "has_wiki": True
    }
    
    print(f"Actualizando repositorio {REPO_OWNER}/{REPO_NAME}...")
    response = requests.patch(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print("✅ Descripción actualizada exitosamente!")
        print(f"📝 Nueva descripción: {NEW_DESCRIPTION}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.json())
    
    return response

def update_topics():
    """Actualiza los topics del repositorio."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/topics"
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.mercy-preview+json"
    }
    
    data = {
        "names": TOPICS
    }
    
    print(f"\nActualizando topics...")
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print("✅ Topics actualizados exitosamente!")
        print(f"🏷️  Topics: {', '.join(TOPICS)}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.json())
    
    return response

if __name__ == "__main__":
    print("=" * 60)
    print("Actualizando información del repositorio en GitHub")
    print("=" * 60)
    
    # Actualizar descripción
    update_repo_info()
    
    # Actualizar topics
    update_topics()
    
    print("\n" + "=" * 60)
    print("✅ Actualización completada!")
    print("=" * 60)
    print(f"\nVisita: https://github.com/{REPO_OWNER}/{REPO_NAME}")
