# -*- coding: utf-8 -*-
"""record_file 극한 테스트 - 100가지 시나리오"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.tracking import record_file, list_files


@pytest.fixture
def temp_project():
    """임시 프로젝트 생성"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def project_with_created(temp_project):
    """created.md가 있는 프로젝트"""
    files_dir = Path(temp_project) / ".claude" / "files"
    files_dir.mkdir(parents=True)
    created_md = files_dir / "created.md"
    created_md.write_text("""# Created Files

> Test project

---

## Files

| 파일경로 | 목적 | 삭제가능 |
|----------|------|----------|

---

## 생성 기록

| 날짜 | 세션 | 파일 |
|------|------|------|
""", encoding='utf-8')
    return temp_project


class TestRecordFileBasic:
    """기본 기능 테스트 (1-20)"""

    @pytest.mark.asyncio
    async def test_01_create_new_file(self, temp_project):
        """1. 새 파일 기록"""
        result = await record_file(temp_project, "src/main.py", "Main entry point")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_02_file_appears_in_created_md(self, temp_project):
        """2. created.md에 파일 추가 확인"""
        await record_file(temp_project, "src/app.py", "Application")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "src/app.py" in content

    @pytest.mark.asyncio
    async def test_03_purpose_recorded(self, temp_project):
        """3. 목적 기록 확인"""
        await record_file(temp_project, "src/utils.py", "Utility functions")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "Utility functions" in content

    @pytest.mark.asyncio
    async def test_04_deletable_false(self, temp_project):
        """4. 삭제 불가 마크 (❌)"""
        await record_file(temp_project, "src/core.py", "Core", deletable=False)
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "❌" in content

    @pytest.mark.asyncio
    async def test_05_deletable_true(self, temp_project):
        """5. 삭제 가능 마크 (⚠️)"""
        await record_file(temp_project, "temp/cache.py", "Cache", deletable=True)
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "⚠️" in content

    @pytest.mark.asyncio
    async def test_06_session_recorded(self, temp_project):
        """6. 세션명 기록"""
        await record_file(temp_project, "src/api.py", "API", session="v1.0")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "v1.0" in content

    @pytest.mark.asyncio
    async def test_07_default_session(self, temp_project):
        """7. 기본 세션명 (auto)"""
        await record_file(temp_project, "src/db.py", "Database")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "auto" in content

    @pytest.mark.asyncio
    async def test_08_duplicate_detection(self, temp_project):
        """8. 중복 감지"""
        await record_file(temp_project, "src/dup.py", "First")
        result = await record_file(temp_project, "src/dup.py", "Second")
        assert "Already recorded" in result[0].text

    @pytest.mark.asyncio
    async def test_09_creates_directory(self, temp_project):
        """9. .claude/files 디렉토리 자동 생성"""
        await record_file(temp_project, "new.py", "New file")
        files_dir = Path(temp_project) / ".claude" / "files"
        assert files_dir.exists()

    @pytest.mark.asyncio
    async def test_10_creates_template(self, temp_project):
        """10. created.md 템플릿 자동 생성"""
        await record_file(temp_project, "first.py", "First file")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        assert created_md.exists()
        content = created_md.read_text(encoding='utf-8')
        assert "# Created Files" in content

    @pytest.mark.asyncio
    async def test_11_multiple_files(self, temp_project):
        """11. 여러 파일 연속 기록"""
        for i in range(5):
            await record_file(temp_project, f"src/file{i}.py", f"File {i}")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        for i in range(5):
            assert f"file{i}.py" in content

    @pytest.mark.asyncio
    async def test_12_nested_path(self, temp_project):
        """12. 중첩 경로"""
        await record_file(temp_project, "src/components/ui/Button.tsx", "Button component")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "src/components/ui/Button.tsx" in content

    @pytest.mark.asyncio
    async def test_13_special_chars_in_purpose(self, temp_project):
        """13. 목적에 특수문자"""
        await record_file(temp_project, "src/special.py", "Handle <, >, & chars")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "Handle <, >, & chars" in content

    @pytest.mark.asyncio
    async def test_14_korean_purpose(self, temp_project):
        """14. 한글 목적"""
        await record_file(temp_project, "src/korean.py", "한글 테스트 파일")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "한글 테스트 파일" in content

    @pytest.mark.asyncio
    async def test_15_emoji_in_purpose(self, temp_project):
        """15. 이모지 목적"""
        await record_file(temp_project, "src/emoji.py", "🚀 Rocket feature")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "🚀" in content

    @pytest.mark.asyncio
    async def test_16_long_purpose(self, temp_project):
        """16. 긴 목적 설명"""
        long_purpose = "A" * 200
        await record_file(temp_project, "src/long.py", long_purpose)
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert long_purpose in content

    @pytest.mark.asyncio
    async def test_17_typescript_file(self, temp_project):
        """17. TypeScript 파일"""
        await record_file(temp_project, "src/index.ts", "TypeScript entry")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "index.ts" in content

    @pytest.mark.asyncio
    async def test_18_json_file(self, temp_project):
        """18. JSON 파일"""
        await record_file(temp_project, "config/settings.json", "Configuration")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "settings.json" in content

    @pytest.mark.asyncio
    async def test_19_markdown_file(self, temp_project):
        """19. Markdown 파일"""
        await record_file(temp_project, "docs/README.md", "Documentation")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "README.md" in content

    @pytest.mark.asyncio
    async def test_20_hidden_file(self, temp_project):
        """20. 숨김 파일"""
        await record_file(temp_project, ".env", "Environment variables")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert ".env" in content


class TestRecordFileEdgeCases:
    """엣지 케이스 테스트 (21-40)"""

    @pytest.mark.asyncio
    async def test_21_empty_purpose(self, temp_project):
        """21. 빈 목적"""
        await record_file(temp_project, "src/empty.py", "")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        assert created_md.exists()

    @pytest.mark.asyncio
    async def test_22_whitespace_purpose(self, temp_project):
        """22. 공백 목적"""
        await record_file(temp_project, "src/space.py", "   ")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        assert created_md.exists()

    @pytest.mark.asyncio
    async def test_23_pipe_in_purpose(self, temp_project):
        """23. 파이프 문자 (테이블 깨짐 방지)"""
        await record_file(temp_project, "src/pipe.py", "A | B | C")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        # 파이프가 있어도 파일이 기록되어야 함
        assert "pipe.py" in content

    @pytest.mark.asyncio
    async def test_24_newline_in_purpose(self, temp_project):
        """24. 개행문자 목적"""
        await record_file(temp_project, "src/newline.py", "Line1\nLine2")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "newline.py" in content

    @pytest.mark.asyncio
    async def test_25_backtick_in_path(self, temp_project):
        """25. 백틱 경로"""
        await record_file(temp_project, "src/`special`.py", "Special chars")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "special" in content

    @pytest.mark.asyncio
    async def test_26_dots_in_path(self, temp_project):
        """26. 여러 점 경로"""
        await record_file(temp_project, "src/file.test.spec.py", "Test file")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "file.test.spec.py" in content

    @pytest.mark.asyncio
    async def test_27_uppercase_extension(self, temp_project):
        """27. 대문자 확장자"""
        await record_file(temp_project, "src/Main.PY", "Main file")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "Main.PY" in content

    @pytest.mark.asyncio
    async def test_28_no_extension(self, temp_project):
        """28. 확장자 없음"""
        await record_file(temp_project, "Makefile", "Build script")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "Makefile" in content

    @pytest.mark.asyncio
    async def test_29_very_long_path(self, temp_project):
        """29. 매우 긴 경로"""
        long_path = "src/" + "/".join(["dir"] * 20) + "/file.py"
        await record_file(temp_project, long_path, "Deep nested")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "file.py" in content

    @pytest.mark.asyncio
    async def test_30_windows_path_separator(self, temp_project):
        """30. 윈도우 경로 구분자"""
        await record_file(temp_project, "src\\windows\\path.py", "Windows path")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "path.py" in content

    @pytest.mark.asyncio
    async def test_31_mixed_path_separators(self, temp_project):
        """31. 혼합 경로 구분자"""
        await record_file(temp_project, "src/mixed\\path/file.py", "Mixed")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "file.py" in content

    @pytest.mark.asyncio
    async def test_32_relative_path_dots(self, temp_project):
        """32. 상대 경로 (..)"""
        await record_file(temp_project, "../outside.py", "Outside project")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "outside.py" in content

    @pytest.mark.asyncio
    async def test_33_current_dir_prefix(self, temp_project):
        """33. 현재 디렉토리 (./)"""
        await record_file(temp_project, "./src/current.py", "Current dir")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "current.py" in content

    @pytest.mark.asyncio
    async def test_34_space_in_path(self, temp_project):
        """34. 경로에 공백"""
        await record_file(temp_project, "src/my file.py", "Spaced file")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "my file.py" in content

    @pytest.mark.asyncio
    async def test_35_unicode_path(self, temp_project):
        """35. 유니코드 경로"""
        await record_file(temp_project, "src/한글파일.py", "Korean filename")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "한글파일.py" in content

    @pytest.mark.asyncio
    async def test_36_session_with_spaces(self, temp_project):
        """36. 세션명에 공백"""
        await record_file(temp_project, "src/sess.py", "Session test", session="Phase 1 Complete")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "Phase 1 Complete" in content

    @pytest.mark.asyncio
    async def test_37_session_korean(self, temp_project):
        """37. 한글 세션명"""
        await record_file(temp_project, "src/ko_sess.py", "Korean session", session="1단계 완료")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "1단계 완료" in content

    @pytest.mark.asyncio
    async def test_38_session_with_emoji(self, temp_project):
        """38. 이모지 세션명"""
        await record_file(temp_project, "src/emoji_sess.py", "Emoji session", session="🎉 Launch")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "🎉" in content

    @pytest.mark.asyncio
    async def test_39_concurrent_writes(self, temp_project):
        """39. 동시 쓰기 (순차 실행)"""
        tasks = []
        for i in range(10):
            tasks.append(record_file(temp_project, f"src/concurrent{i}.py", f"Concurrent {i}"))
        results = await asyncio.gather(*tasks)
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        # 최소 1개는 성공해야 함
        assert "concurrent" in content

    @pytest.mark.asyncio
    async def test_40_existing_created_md(self, project_with_created):
        """40. 기존 created.md에 추가"""
        await record_file(project_with_created, "src/new.py", "New file")
        created_md = Path(project_with_created) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "new.py" in content
        assert "Test project" in content  # 기존 내용 유지


class TestRecordFileFileTypes:
    """다양한 파일 타입 테스트 (41-60)"""

    @pytest.mark.asyncio
    async def test_41_python(self, temp_project):
        """41. Python"""
        result = await record_file(temp_project, "src/main.py", "Python file")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_42_javascript(self, temp_project):
        """42. JavaScript"""
        result = await record_file(temp_project, "src/index.js", "JavaScript")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_43_typescript(self, temp_project):
        """43. TypeScript"""
        result = await record_file(temp_project, "src/app.ts", "TypeScript")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_44_tsx(self, temp_project):
        """44. TSX"""
        result = await record_file(temp_project, "src/Component.tsx", "React TSX")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_45_jsx(self, temp_project):
        """45. JSX"""
        result = await record_file(temp_project, "src/Component.jsx", "React JSX")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_46_rust(self, temp_project):
        """46. Rust"""
        result = await record_file(temp_project, "src/main.rs", "Rust")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_47_go(self, temp_project):
        """47. Go"""
        result = await record_file(temp_project, "main.go", "Go")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_48_java(self, temp_project):
        """48. Java"""
        result = await record_file(temp_project, "src/Main.java", "Java")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_49_kotlin(self, temp_project):
        """49. Kotlin"""
        result = await record_file(temp_project, "src/Main.kt", "Kotlin")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_50_swift(self, temp_project):
        """50. Swift"""
        result = await record_file(temp_project, "Sources/main.swift", "Swift")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_51_cpp(self, temp_project):
        """51. C++"""
        result = await record_file(temp_project, "src/main.cpp", "C++")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_52_c(self, temp_project):
        """52. C"""
        result = await record_file(temp_project, "src/main.c", "C")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_53_header(self, temp_project):
        """53. Header"""
        result = await record_file(temp_project, "include/header.h", "Header")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_54_ruby(self, temp_project):
        """54. Ruby"""
        result = await record_file(temp_project, "app.rb", "Ruby")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_55_php(self, temp_project):
        """55. PHP"""
        result = await record_file(temp_project, "index.php", "PHP")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_56_html(self, temp_project):
        """56. HTML"""
        result = await record_file(temp_project, "index.html", "HTML")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_57_css(self, temp_project):
        """57. CSS"""
        result = await record_file(temp_project, "styles.css", "CSS")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_58_scss(self, temp_project):
        """58. SCSS"""
        result = await record_file(temp_project, "styles.scss", "SCSS")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_59_yaml(self, temp_project):
        """59. YAML"""
        result = await record_file(temp_project, "config.yaml", "YAML config")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_60_toml(self, temp_project):
        """60. TOML"""
        result = await record_file(temp_project, "pyproject.toml", "TOML config")
        assert "✅" in result[0].text


class TestRecordFileConfigFiles:
    """설정 파일 테스트 (61-75)"""

    @pytest.mark.asyncio
    async def test_61_gitignore(self, temp_project):
        """61. .gitignore"""
        result = await record_file(temp_project, ".gitignore", "Git ignore rules")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_62_dockerignore(self, temp_project):
        """62. .dockerignore"""
        result = await record_file(temp_project, ".dockerignore", "Docker ignore")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_63_dockerfile(self, temp_project):
        """63. Dockerfile"""
        result = await record_file(temp_project, "Dockerfile", "Docker image")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_64_docker_compose(self, temp_project):
        """64. docker-compose.yml"""
        result = await record_file(temp_project, "docker-compose.yml", "Docker compose")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_65_package_json(self, temp_project):
        """65. package.json"""
        result = await record_file(temp_project, "package.json", "NPM package")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_66_tsconfig(self, temp_project):
        """66. tsconfig.json"""
        result = await record_file(temp_project, "tsconfig.json", "TypeScript config")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_67_eslintrc(self, temp_project):
        """67. .eslintrc.js"""
        result = await record_file(temp_project, ".eslintrc.js", "ESLint config")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_68_prettierrc(self, temp_project):
        """68. .prettierrc"""
        result = await record_file(temp_project, ".prettierrc", "Prettier config")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_69_env_example(self, temp_project):
        """69. .env.example"""
        result = await record_file(temp_project, ".env.example", "Environment template")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_70_requirements_txt(self, temp_project):
        """70. requirements.txt"""
        result = await record_file(temp_project, "requirements.txt", "Python deps")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_71_cargo_toml(self, temp_project):
        """71. Cargo.toml"""
        result = await record_file(temp_project, "Cargo.toml", "Rust package")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_72_go_mod(self, temp_project):
        """72. go.mod"""
        result = await record_file(temp_project, "go.mod", "Go module")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_73_gemfile(self, temp_project):
        """73. Gemfile"""
        result = await record_file(temp_project, "Gemfile", "Ruby deps")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_74_claude_md(self, temp_project):
        """74. CLAUDE.md"""
        result = await record_file(temp_project, "CLAUDE.md", "Claude rules")
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_75_wrangler_toml(self, temp_project):
        """75. wrangler.toml"""
        result = await record_file(temp_project, "wrangler.toml", "Cloudflare config")
        assert "✅" in result[0].text


class TestListFiles:
    """list_files 테스트 (76-85)"""

    @pytest.mark.asyncio
    async def test_76_list_empty(self, temp_project):
        """76. 빈 프로젝트"""
        result = await list_files(temp_project)
        assert "No files recorded" in result[0].text

    @pytest.mark.asyncio
    async def test_77_list_after_record(self, temp_project):
        """77. 기록 후 목록"""
        await record_file(temp_project, "src/main.py", "Main")
        result = await list_files(temp_project)
        assert "main.py" in result[0].text

    @pytest.mark.asyncio
    async def test_78_list_multiple(self, temp_project):
        """78. 여러 파일 목록"""
        await record_file(temp_project, "a.py", "A")
        await record_file(temp_project, "b.py", "B")
        await record_file(temp_project, "c.py", "C")
        result = await list_files(temp_project)
        assert "a.py" in result[0].text
        assert "b.py" in result[0].text
        assert "c.py" in result[0].text

    @pytest.mark.asyncio
    async def test_79_list_count(self, temp_project):
        """79. 파일 개수 표시"""
        await record_file(temp_project, "1.py", "1")
        await record_file(temp_project, "2.py", "2")
        result = await list_files(temp_project)
        assert "Recorded Files" in result[0].text

    @pytest.mark.asyncio
    async def test_80_list_existing(self, project_with_created):
        """80. 기존 파일 목록"""
        result = await list_files(project_with_created)
        assert "Created Files" in result[0].text

    @pytest.mark.asyncio
    async def test_81_list_with_purpose(self, temp_project):
        """81. 목적 포함 목록"""
        await record_file(temp_project, "api.py", "REST API endpoints")
        result = await list_files(temp_project)
        assert "REST API" in result[0].text

    @pytest.mark.asyncio
    async def test_82_list_deletable_mark(self, temp_project):
        """82. 삭제 가능 마크 목록"""
        await record_file(temp_project, "temp.py", "Temp", deletable=True)
        result = await list_files(temp_project)
        assert "⚠️" in result[0].text

    @pytest.mark.asyncio
    async def test_83_list_session_info(self, temp_project):
        """83. 세션 정보 목록"""
        await record_file(temp_project, "v1.py", "V1", session="Phase 1")
        result = await list_files(temp_project)
        assert "Phase 1" in result[0].text

    @pytest.mark.asyncio
    async def test_84_list_date_recorded(self, temp_project):
        """84. 날짜 표시"""
        await record_file(temp_project, "dated.py", "Dated")
        result = await list_files(temp_project)
        assert "2026" in result[0].text  # 현재 연도

    @pytest.mark.asyncio
    async def test_85_list_markdown_format(self, temp_project):
        """85. 마크다운 형식"""
        await record_file(temp_project, "md.py", "Markdown test")
        result = await list_files(temp_project)
        assert "|" in result[0].text  # 테이블 형식


class TestRecordFileStress:
    """스트레스 테스트 (86-100)"""

    @pytest.mark.asyncio
    async def test_86_record_50_files(self, temp_project):
        """86. 50개 파일 기록"""
        for i in range(50):
            await record_file(temp_project, f"src/file_{i:03d}.py", f"File {i}")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "file_049.py" in content

    @pytest.mark.asyncio
    async def test_87_record_with_all_options(self, temp_project):
        """87. 모든 옵션 사용"""
        result = await record_file(
            path=temp_project,
            file_path="src/full_options.py",
            purpose="Full options test with very long description",
            deletable=True,
            session="Complete Test Session v1.0"
        )
        assert "✅" in result[0].text

    @pytest.mark.asyncio
    async def test_88_rapid_succession(self, temp_project):
        """88. 빠른 연속 호출"""
        for i in range(20):
            await record_file(temp_project, f"rapid/{i}.py", f"Rapid {i}")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "19.py" in content

    @pytest.mark.asyncio
    async def test_89_mixed_types_bulk(self, temp_project):
        """89. 혼합 타입 대량"""
        extensions = ['.py', '.js', '.ts', '.go', '.rs', '.java', '.rb', '.php', '.c', '.cpp']
        for i, ext in enumerate(extensions):
            await record_file(temp_project, f"src/file{i}{ext}", f"Type {ext}")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        for ext in extensions:
            assert ext in content

    @pytest.mark.asyncio
    async def test_90_unicode_stress(self, temp_project):
        """90. 유니코드 스트레스"""
        names = ["日本語", "中文", "한글", "العربية", "עברית", "Ελληνικά", "Русский", "ไทย"]
        for name in names:
            await record_file(temp_project, f"src/{name}.py", f"{name} file")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        for name in names:
            assert name in content

    @pytest.mark.asyncio
    async def test_91_emoji_stress(self, temp_project):
        """91. 이모지 스트레스"""
        emojis = ["🚀", "💡", "🔥", "⚡", "🎉", "✨", "🔧", "📦"]
        for emoji in emojis:
            await record_file(temp_project, f"src/{emoji}.py", f"{emoji} feature")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        for emoji in emojis:
            assert emoji in content

    @pytest.mark.asyncio
    async def test_92_deep_nesting(self, temp_project):
        """92. 깊은 중첩"""
        for depth in range(1, 11):
            path = "/".join(["d"] * depth) + "/file.py"
            await record_file(temp_project, path, f"Depth {depth}")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "d/d/d/d/d/d/d/d/d/d/file.py" in content

    @pytest.mark.asyncio
    async def test_93_special_session_chars(self, temp_project):
        """93. 특수문자 세션"""
        sessions = ["v1.0-beta", "feature/auth", "fix#123", "user@email"]
        for i, sess in enumerate(sessions):
            await record_file(temp_project, f"src/s{i}.py", "Session test", session=sess)
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        for sess in sessions:
            assert sess in content

    @pytest.mark.asyncio
    async def test_94_long_filename(self, temp_project):
        """94. 긴 파일명"""
        long_name = "a" * 100 + ".py"
        await record_file(temp_project, f"src/{long_name}", "Long name")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert long_name in content

    @pytest.mark.asyncio
    async def test_95_all_deletable_true(self, temp_project):
        """95. 모두 삭제 가능"""
        for i in range(10):
            await record_file(temp_project, f"temp/{i}.py", f"Temp {i}", deletable=True)
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert content.count("⚠️") >= 10

    @pytest.mark.asyncio
    async def test_96_mixed_deletable(self, temp_project):
        """96. 혼합 삭제 가능"""
        for i in range(10):
            await record_file(temp_project, f"mix/{i}.py", f"Mix {i}", deletable=(i % 2 == 0))
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "⚠️" in content
        assert "❌" in content

    @pytest.mark.asyncio
    async def test_97_same_name_different_dirs(self, temp_project):
        """97. 같은 이름 다른 디렉토리"""
        dirs = ["src", "lib", "test", "utils", "core"]
        for d in dirs:
            await record_file(temp_project, f"{d}/index.py", f"{d} index")
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        for d in dirs:
            assert f"{d}/index.py" in content

    @pytest.mark.asyncio
    async def test_98_record_then_list(self, temp_project):
        """98. 기록 후 목록 확인"""
        files = ["a.py", "b.py", "c.py", "d.py", "e.py"]
        for f in files:
            await record_file(temp_project, f"src/{f}", f"File {f}")
        result = await list_files(temp_project)
        for f in files:
            assert f in result[0].text

    @pytest.mark.asyncio
    async def test_99_full_workflow(self, temp_project):
        """99. 전체 워크플로우"""
        # 1. 여러 파일 기록
        await record_file(temp_project, "src/main.py", "Main entry", session="Init")
        await record_file(temp_project, "src/utils.py", "Utilities", session="Init")
        await record_file(temp_project, "tests/test_main.py", "Tests", deletable=True, session="Testing")

        # 2. 중복 시도
        dup_result = await record_file(temp_project, "src/main.py", "Duplicate")
        assert "Already" in dup_result[0].text

        # 3. 목록 확인
        list_result = await list_files(temp_project)
        assert "main.py" in list_result[0].text
        assert "utils.py" in list_result[0].text
        assert "test_main.py" in list_result[0].text

    @pytest.mark.asyncio
    async def test_100_extreme_purpose(self, temp_project):
        """100. 극한 목적 테스트"""
        extreme_purpose = "🚀 " + "A" * 500 + " 한글테스트 " + "B" * 500 + " 🎉"
        result = await record_file(temp_project, "src/extreme.py", extreme_purpose)
        assert "✅" in result[0].text
        created_md = Path(temp_project) / ".claude" / "files" / "created.md"
        content = created_md.read_text(encoding='utf-8')
        assert "extreme.py" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
