#!/usr/bin/env python3
"""
Script de limpieza para el repositorio RAG.
Elimina archivos temporales, caché y verifica la estructura.
"""

import os
import shutil
import sys
from pathlib import Path

def clean_pycache():
    """Eliminar directorios __pycache__"""
    print("🧹 Limpiando __pycache__...")
    pycache_dirs = list(Path(".").rglob("__pycache__"))
    for dir_path in pycache_dirs:
        try:
            shutil.rmtree(dir_path)
            print(f"  ✓ Eliminado: {dir_path}")
        except Exception as e:
            print(f"  ✗ Error eliminando {dir_path}: {e}")

def clean_pyc_files():
    """Eliminar archivos .pyc"""
    print("\n🧹 Limpiando archivos .pyc...")
    pyc_files = list(Path(".").rglob("*.pyc"))
    for file_path in pyc_files:
        try:
            file_path.unlink()
            print(f"  ✓ Eliminado: {file_path}")
        except Exception as e:
            print(f"  ✗ Error eliminando {file_path}: {e}")

def verify_gitignore():
    """Verificar que .gitignore esté configurado correctamente"""
    print("\n🔍 Verificando .gitignore...")
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        print("  ✗ .gitignore no encontrado")
        return False
    
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_patterns = ['.env', '.venv/', '__pycache__/', '*.pyc']
    missing = []
    for pattern in required_patterns:
        if pattern not in content:
            missing.append(pattern)
    
    if missing:
        print(f"  ⚠️ Faltan patrones en .gitignore: {missing}")
        return False
    else:
        print("  ✓ .gitignore configurado correctamente")
        return True

def verify_env_example():
    """Verificar que .env.example exista y no contenga claves reales"""
    print("\n🔍 Verificando .env.example...")
    example_path = Path(".env.example")
    actual_path = Path(".env")
    
    if not example_path.exists():
        print("  ✗ .env.example no encontrado")
        return False
    
    # Verificar que no contenga claves reales
    with open(example_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sensitive_keywords = ['gsk_', 'eyJ', 'sk-']
    found_sensitive = []
    for keyword in sensitive_keywords:
        if keyword in content:
            found_sensitive.append(keyword)
    
    if found_sensitive:
        print(f"  ⚠️ Posibles claves sensibles encontradas en .env.example: {found_sensitive}")
        return False
    else:
        print("  ✓ .env.example seguro (sin claves reales)")
        return True

def check_structure():
    """Verificar estructura básica del proyecto"""
    print("\n📁 Verificando estructura del proyecto...")
    
    required_dirs = ['app', 'data/pdfs']
    required_files = [
        'README.md',
        'requirements.txt',
        'chainlit.py',
        '.gitignore',
        '.env.example'
    ]
    
    all_ok = True
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  ✓ Directorio: {dir_path}")
        else:
            print(f"  ✗ Directorio faltante: {dir_path}")
            all_ok = False
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✓ Archivo: {file_path}")
        else:
            print(f"  ✗ Archivo faltante: {file_path}")
            all_ok = False
    
    return all_ok

def main():
    print("=" * 50)
    print("🧹 LIMPIEZA DE REPOSITORIO RAG")
    print("=" * 50)
    
    # Ejecutar limpieza
    clean_pycache()
    clean_pyc_files()
    
    # Ejecutar verificaciones
    gitignore_ok = verify_gitignore()
    env_ok = verify_env_example()
    structure_ok = check_structure()
    
    print("\n" + "=" * 50)
    print("📋 RESUMEN")
    print("=" * 50)
    
    all_ok = gitignore_ok and env_ok and structure_ok
    
    if all_ok:
        print("✅ ¡Repositorio limpio y listo para Git!")
        print("\n📝 Siguientes pasos:")
        print("1. git add .")
        print("2. git commit -m 'Initial commit: RAG System'")
        print("3. git push")
    else:
        print("⚠️  Se encontraron problemas que necesitan atención.")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())