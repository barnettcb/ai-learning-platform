(() => {
  const button = document.getElementById('nav-toggle');
  const sidebar = document.getElementById('sidebar');
  if (button && sidebar) {
    button.addEventListener('click', () => {
      const open = sidebar.classList.toggle('open');
      button.setAttribute('aria-expanded', String(open));
    });
  }


  const normalizePath = (value) => {
    const path = value.replace(/\\/g, '/').replace(/\/index\.html$/, '/');
    return path.endsWith('/') ? path : `${path}`;
  };
  const currentPath = normalizePath(window.location.pathname);
  document.querySelectorAll('.sidebar a').forEach((link) => {
    const linkPath = normalizePath(new URL(link.href, window.location.href).pathname);
    const exact = linkPath === currentPath;
    const moduleParent = linkPath.includes('/modules/module-') && currentPath.startsWith(linkPath);
    if (exact || moduleParent) {
      link.classList.add('is-current');
      link.setAttribute('aria-current', exact ? 'page' : 'location');
    }
  });
  const currentModuleLink = document.querySelector('.nav-module a.is-current');
  if (currentModuleLink) currentModuleLink.closest('details')?.setAttribute('open', '');

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && sidebar && sidebar.classList.contains('open')) {
      sidebar.classList.remove('open');
      if (button) {
        button.setAttribute('aria-expanded', 'false');
        button.focus();
      }
    }
  });

  const progressKey = 'practical-ai-learning-completed-v1';
  const bookmarksKey = 'practical-ai-learning-bookmarks-v1';
  const notesKey = 'practical-ai-learning-notes-v1';
  const responsesKey = 'practical-ai-learning-responses-v1';

  const readArray = (key) => {
    try {
      const value = JSON.parse(localStorage.getItem(key) || '[]');
      return Array.isArray(value) ? value : [];
    } catch (_) {
      return [];
    }
  };
  const readObject = (key) => {
    try {
      const value = JSON.parse(localStorage.getItem(key) || '{}');
      return value && typeof value === 'object' && !Array.isArray(value) ? value : {};
    } catch (_) {
      return {};
    }
  };
  const writeArray = (key, values) => {
    localStorage.setItem(key, JSON.stringify([...values]));
  };
  const writeObject = (key, value) => {
    localStorage.setItem(key, JSON.stringify(value));
  };
  const sanitizeImportedValue = (value, depth = 0) => {
    if (depth > 4) return undefined;
    if (typeof value === 'string') return value.slice(0, 20000);
    if (typeof value === 'boolean' || (typeof value === 'number' && Number.isFinite(value))) return value;
    if (Array.isArray(value)) {
      return value.slice(0, 100).map((item) => sanitizeImportedValue(item, depth + 1)).filter((item) => item !== undefined);
    }
    if (value && typeof value === 'object') {
      const result = {};
      Object.entries(value).slice(0, 200).forEach(([key, item]) => {
        const clean = sanitizeImportedValue(item, depth + 1);
        if (clean !== undefined) result[String(key).slice(0, 120)] = clean;
      });
      return result;
    }
    return undefined;
  };

  const readProgress = () => new Set(readArray(progressKey));
  const writeProgress = (completed) => writeArray(progressKey, completed);
  const readBookmarks = () => new Set(readArray(bookmarksKey));
  const writeBookmarks = (bookmarks) => writeArray(bookmarksKey, bookmarks);
  const readNotes = () => readObject(notesKey);
  const writeNotes = (notes) => writeObject(notesKey, notes);
  const readResponses = () => readObject(responsesKey);
  const writeResponses = (responses) => writeObject(responsesKey, responses);

  const lessons = Array.isArray(window.PRACTICAL_AI_LESSONS)
    ? window.PRACTICAL_AI_LESSONS
    : [];
  const milestones = Array.isArray(window.PRACTICAL_AI_MILESTONES)
    ? window.PRACTICAL_AI_MILESTONES
    : [];
  const searchIndex = Array.isArray(window.PRACTICAL_AI_SEARCH_INDEX)
    ? window.PRACTICAL_AI_SEARCH_INDEX
    : [];
  const guidedPath = Array.isArray(window.PRACTICAL_AI_GUIDED_PATH)
    ? window.PRACTICAL_AI_GUIDED_PATH
    : [...lessons, ...milestones];

  const pageId = document.body.dataset.pageId;
  const pageTitle = document.body.dataset.pageTitle || document.title;
  const pageKind = document.body.dataset.pageKind || 'content';

  const completionButton = document.querySelector('[data-completion-toggle]');
  if (pageId && completionButton) {
    const completed = readProgress();
    const render = () => {
      const isComplete = completed.has(pageId);
      completionButton.textContent = isComplete
        ? completionButton.dataset.labelComplete
        : completionButton.dataset.labelIncomplete;
      completionButton.setAttribute('aria-pressed', String(isComplete));
      completionButton.classList.toggle('is-complete', isComplete);
    };
    completionButton.addEventListener('click', () => {
      if (completed.has(pageId)) completed.delete(pageId);
      else completed.add(pageId);
      writeProgress(completed);
      render();
    });
    render();
  }

  document.querySelectorAll('[data-lesson-check]').forEach((check) => {
    const checkId = check.dataset.checkId;
    const answer = Number(check.dataset.answer);
    const button = check.querySelector('[data-lesson-check-submit]');
    const feedback = check.querySelector('[data-lesson-check-feedback]');
    const stored = readResponses();
    const saved = stored[checkId];
    if (saved && Number.isInteger(saved.choice)) {
      const input = check.querySelector(`input[value="${saved.choice}"]`);
      if (input) input.checked = true;
      check.classList.add(saved.correct ? 'is-correct' : 'is-incorrect');
      if (feedback) feedback.textContent = `${saved.correct ? 'Correct.' : 'Not quite.'} ${feedback.dataset.explanation}`;
    }
    button?.addEventListener('click', () => {
      const selected = check.querySelector('input[type="radio"]:checked');
      check.classList.remove('is-correct', 'is-incorrect');
      if (!selected) {
        if (feedback) feedback.textContent = 'Choose an answer first.';
        return;
      }
      const choice = Number(selected.value);
      const correct = choice === answer;
      check.classList.add(correct ? 'is-correct' : 'is-incorrect');
      if (feedback) feedback.textContent = `${correct ? 'Correct.' : 'Not quite.'} ${feedback.dataset.explanation}`;
      const responses = readResponses();
      responses[checkId] = { choice, correct };
      writeResponses(responses);
    });
  });

  const assessmentForm = document.querySelector('[data-assessment-form]');
  if (pageId && assessmentForm) {
    const result = assessmentForm.querySelector('[data-assessment-result]');
    const questions = [...assessmentForm.querySelectorAll('[data-question]')];
    const savedAssessment = readResponses()[pageId];
    if (savedAssessment && Array.isArray(savedAssessment.choices)) {
      questions.forEach((question, index) => {
        const value = savedAssessment.choices[index];
        const input = question.querySelector(`input[value="${value}"]`);
        const expected = Number(question.dataset.answer);
        const explanation = question.querySelector('[data-explanation]');
        if (input) {
          input.checked = true;
          const isCorrect = Number(value) === expected;
          question.classList.add(isCorrect ? 'is-correct' : 'is-incorrect');
          if (explanation) explanation.hidden = false;
        }
      });
      if (result && Number.isInteger(savedAssessment.score)) {
        result.textContent = `Last attempt: ${savedAssessment.score} of ${questions.length} correct.${savedAssessment.passed ? ' Readiness check complete ✓' : ' Use the review links below, then retry when ready.'}`;
        result.classList.toggle('is-passed', Boolean(savedAssessment.passed));
      }
    } else if (readProgress().has(pageId) && result) {
      result.textContent = 'Previously completed ✓ You may retake this check at any time.';
      result.classList.add('is-passed');
    }
    assessmentForm.addEventListener('submit', (event) => {
      event.preventDefault();
      let answered = 0;
      let correct = 0;
      const choices = [];
      questions.forEach((question) => {
        const selected = question.querySelector('input[type="radio"]:checked');
        const expected = Number(question.dataset.answer);
        const explanation = question.querySelector('[data-explanation]');
        question.classList.remove('is-correct', 'is-incorrect');
        if (selected) {
          answered += 1;
          const choice = Number(selected.value);
          choices.push(choice);
          const isCorrect = choice === expected;
          if (isCorrect) correct += 1;
          question.classList.add(isCorrect ? 'is-correct' : 'is-incorrect');
          if (explanation) explanation.hidden = false;
        }
      });
      if (answered !== questions.length) {
        if (result) result.textContent = `Answer all ${questions.length} questions before submitting.`;
        return;
      }
      const passed = correct === questions.length;
      const responses = readResponses();
      const prior = responses[pageId] && typeof responses[pageId] === 'object' ? responses[pageId] : {};
      responses[pageId] = {
        choices,
        score: correct,
        passed,
        attempts: Number(prior.attempts || 0) + 1,
      };
      writeResponses(responses);
      if (passed) {
        const completed = readProgress();
        completed.add(pageId);
        writeProgress(completed);
      }
      if (result) {
        result.textContent = passed
          ? `${correct} of ${questions.length} correct. Readiness check complete ✓`
          : `${correct} of ${questions.length} correct. Read the explanations, revisit the linked lesson if needed, and retry.`;
        result.classList.toggle('is-passed', passed);
      }
    });
  }

  const activity = document.querySelector('[data-interactive-activity]');
  if (pageId && activity) {
    const activityId = activity.dataset.activityId || pageId;
    const inputs = [...activity.querySelectorAll('[data-activity-input]')];
    const count = activity.querySelector('[data-activity-count]');
    const progressBar = activity.querySelector('[data-activity-progress]');
    const progressTrack = progressBar ? progressBar.parentElement : null;
    const status = activity.querySelector('[data-activity-status]');
    const reviewButton = activity.querySelector('[data-activity-review]');
    const clearButton = activity.querySelector('[data-activity-clear]');
    const allResponses = readResponses();
    const saved = allResponses[activityId] && typeof allResponses[activityId] === 'object'
      ? allResponses[activityId]
      : {};

    inputs.forEach((input) => {
      const key = input.dataset.responseKey;
      if (key && typeof saved[key] === 'string') input.value = saved[key];
    });

    const renderActivityProgress = () => {
      const required = inputs.filter((input) => input.dataset.required === 'true');
      const complete = required.filter((input) => input.value.trim()).length;
      const total = required.length;
      const percent = total ? Math.round((complete / total) * 100) : 100;
      if (count) count.textContent = `${complete} of ${total}`;
      if (progressBar) progressBar.style.width = `${percent}%`;
      if (progressTrack) progressTrack.setAttribute('aria-valuenow', String(percent));
      activity.classList.toggle('is-complete', complete === total);
      return { complete, total };
    };

    let activityTimer = null;
    const saveActivity = () => {
      const next = readResponses();
      const values = {};
      inputs.forEach((input) => {
        const key = input.dataset.responseKey;
        if (key && input.value.trim()) values[key] = input.value.slice(0, 20000);
      });
      if (Object.keys(values).length) next[activityId] = values;
      else delete next[activityId];
      writeResponses(next);
      if (status) status.textContent = Object.keys(values).length
        ? 'Worksheet saved in this browser.'
        : 'Worksheet is empty.';
      renderActivityProgress();
    };

    inputs.forEach((input) => {
      input.addEventListener('input', () => {
        window.clearTimeout(activityTimer);
        if (status) status.textContent = 'Saving…';
        activityTimer = window.setTimeout(saveActivity, 220);
        renderActivityProgress();
      });
      input.addEventListener('change', saveActivity);
    });

    if (reviewButton) {
      reviewButton.addEventListener('click', () => {
        const state = renderActivityProgress();
        const firstMissing = inputs.find((input) => input.dataset.required === 'true' && !input.value.trim());
        if (firstMissing) {
          if (status) status.textContent = `${state.total - state.complete} required response${state.total - state.complete === 1 ? '' : 's'} still open.`;
          firstMissing.focus();
        } else if (status) {
          status.textContent = 'All required responses are complete. Compare your work with the evaluation criteria, then mark the task complete below.';
        }
      });
    }

    if (clearButton) {
      clearButton.addEventListener('click', () => {
        if (!window.confirm('Clear every response in this worksheet?')) return;
        inputs.forEach((input) => { input.value = ''; });
        const next = readResponses();
        delete next[activityId];
        writeResponses(next);
        renderActivityProgress();
        if (status) status.textContent = 'Worksheet cleared.';
      });
    }

    renderActivityProgress();
  }


  const capstoneWorkbook = document.querySelector('[data-capstone-workbook]');
  if (pageId && capstoneWorkbook) {
    const fields = [...capstoneWorkbook.querySelectorAll('[data-capstone-input]')];
    const count = capstoneWorkbook.querySelector('[data-capstone-count]');
    const bar = capstoneWorkbook.querySelector('[data-capstone-progress]');
    const status = capstoneWorkbook.querySelector('[data-capstone-status]');
    const review = capstoneWorkbook.querySelector('[data-capstone-review]');
    const saved = readResponses()[pageId] || {};
    fields.forEach((field) => {
      const key = field.dataset.responseKey;
      if (key && typeof saved[key] === 'string') field.value = saved[key];
    });
    const render = () => {
      const complete = fields.filter((field) => field.value.trim()).length;
      const total = fields.length;
      const percent = total ? Math.round((complete / total) * 100) : 0;
      if (count) count.textContent = `${complete} of ${total}`;
      if (bar) bar.style.width = `${percent}%`;
      return { complete, total };
    };
    let timer = null;
    const save = () => {
      const responses = readResponses();
      const values = {};
      fields.forEach((field) => {
        const key = field.dataset.responseKey;
        if (key && field.value.trim()) values[key] = field.value.slice(0, 20000);
      });
      if (Object.keys(values).length) responses[pageId] = values;
      else delete responses[pageId];
      writeResponses(responses);
      if (status) status.textContent = Object.keys(values).length ? 'Capstone plan saved in this browser.' : 'Capstone plan is empty.';
      render();
    };
    fields.forEach((field) => field.addEventListener('input', () => {
      window.clearTimeout(timer);
      if (status) status.textContent = 'Saving…';
      timer = window.setTimeout(save, 220);
      render();
    }));
    review?.addEventListener('click', () => {
      const state = render();
      const missing = fields.find((field) => !field.value.trim());
      if (missing) {
        if (status) status.textContent = `${state.total - state.complete} planning response${state.total - state.complete === 1 ? '' : 's'} still open.`;
        missing.focus();
      } else if (status) {
        status.textContent = 'Your capstone plan is complete. Produce the deliverable, verify it, then mark the capstone complete below.';
      }
    });
    render();
  }

  const diagnosticForm = document.querySelector('[data-initial-assessment]');
  if (diagnosticForm) {
    const diagnosticId = 'initial-self-assessment';
    const questions = [...diagnosticForm.querySelectorAll('[data-diagnostic-question]')];
    const submit = diagnosticForm.querySelector('[data-diagnostic-submit]');
    const result = diagnosticForm.querySelector('[data-diagnostic-result]');
    const savedDiagnostic = readResponses()[diagnosticId] || {};

    const moduleLinks = (question) => String(question.dataset.modules || '')
      .split(';')
      .map((item) => item.split('|'))
      .filter((parts) => parts.length === 2)
      .map(([label, url]) => `<a href="${escapeHtml(url)}">${escapeHtml(label)}</a>`)
      .join(', ');

    const chosenText = (question) => {
      const selected = question.querySelector('input[type="radio"]:checked');
      return selected ? selected.closest('label')?.textContent.trim() || '' : '';
    };

    const preferredText = (question) => {
      const preferred = question.querySelector('input[value="2"]');
      return preferred ? preferred.closest('label')?.textContent.trim() || '' : '';
    };

    const saveDiagnostic = (submitted = false, score = null) => {
      const next = readResponses();
      const values = {};
      questions.forEach((question, index) => {
        const selected = question.querySelector('input[type="radio"]:checked');
        if (selected) values[`q${index + 1}`] = selected.value;
      });
      if (Object.keys(values).length) {
        values.submitted = submitted;
        if (Number.isInteger(score)) values.score = score;
        next[diagnosticId] = values;
      } else {
        delete next[diagnosticId];
      }
      writeResponses(next);
    };

    const clearDiagnosticDisplay = () => {
      questions.forEach((question) => {
        question.classList.remove('is-strong', 'is-developing', 'is-risky');
        const feedback = question.querySelector('[data-diagnostic-feedback]');
        if (feedback) {
          feedback.hidden = true;
          feedback.textContent = '';
        }
      });
      if (result) result.innerHTML = '';
    };

    const renderDiagnostic = () => {
      let score = 0;
      const strengths = [];
      const focusAreas = [];
      questions.forEach((question) => {
        const selected = question.querySelector('input[type="radio"]:checked');
        const value = Number(selected?.value || 0);
        const classification = value === 2 ? 'Strong starting choice' : value === 1 ? 'Developing choice' : 'Risky choice';
        score += value;
        question.classList.remove('is-strong', 'is-developing', 'is-risky');
        question.classList.add(value === 2 ? 'is-strong' : value === 1 ? 'is-developing' : 'is-risky');
        const feedback = question.querySelector('[data-diagnostic-feedback]');
        if (feedback) {
          feedback.hidden = false;
          feedback.innerHTML = `<strong>${classification}.</strong> Your choice: ${escapeHtml(chosenText(question))}<br><strong>Preferred response:</strong> ${escapeHtml(preferredText(question))}<br>${escapeHtml(question.dataset.rationale || '')}<br><strong>Review:</strong> ${moduleLinks(question)}`;
        }
        const item = { title: question.dataset.focusTitle || question.dataset.focus || 'this area', links: moduleLinks(question) };
        if (value === 2) strengths.push(item);
        else focusAreas.push(item);
      });
      const summary = score >= 8
        ? 'You already show strong judgment in most of the situations.'
        : score >= 5
          ? 'You have several sound instincts, with some habits to make more consistent.'
          : 'The foundations will help you slow down the decision process and keep responsibility visible.';
      const list = (items, emptyText) => items.length
        ? `<ul>${items.map((item) => `<li><strong>${escapeHtml(item.title)}</strong>${item.links ? ` — ${item.links}` : ''}</li>`).join('')}</ul>`
        : `<p>${escapeHtml(emptyText)}</p>`;
      if (result) {
        result.innerHTML = `<section class="diagnostic-summary"><p class="eyebrow">Your starting point</p><h3>${score} of 10 points</h3><p>${escapeHtml(summary)}</p><div class="diagnostic-columns"><div><h4>Current strengths</h4>${list(strengths, 'No area reached the preferred response yet. That is a useful baseline, not a failure.')}</div><div><h4>Focus areas</h4>${list(focusAreas, 'No immediate weak area appeared. Complete the full course to make the habits repeatable.')}</div></div><p><strong>Next step:</strong> Everyone begins with <a href="modules/module-01/index.html">Module 1</a> so the program uses one shared foundation.</p></section>`;
      }
      saveDiagnostic(true, score);
    };

    questions.forEach((question, index) => {
      const savedValue = savedDiagnostic[`q${index + 1}`];
      if (typeof savedValue === 'string') {
        const choice = question.querySelector(`input[value="${savedValue}"]`);
        if (choice) choice.checked = true;
      }
      question.addEventListener('change', () => {
        clearDiagnosticDisplay();
        saveDiagnostic(false, null);
      });
    });

    if (savedDiagnostic.submitted && questions.every((question) => question.querySelector('input[type="radio"]:checked'))) {
      renderDiagnostic();
    }

    submit?.addEventListener('click', () => {
      const unanswered = questions.find((question) => !question.querySelector('input[type="radio"]:checked'));
      if (unanswered) {
        if (result) result.textContent = 'Answer all five questions to see your starting point.';
        unanswered.querySelector('input')?.focus();
        return;
      }
      renderDiagnostic();
    });
  }


  const bookmarkButton = document.querySelector('[data-bookmark-toggle]');
  if (pageId && bookmarkButton) {
    const bookmarks = readBookmarks();
    const render = () => {
      const saved = bookmarks.has(pageId);
      bookmarkButton.textContent = saved ? 'Bookmarked ✓' : 'Bookmark page';
      bookmarkButton.setAttribute('aria-pressed', String(saved));
      bookmarkButton.classList.toggle('is-bookmarked', saved);
    };
    bookmarkButton.addEventListener('click', () => {
      if (bookmarks.has(pageId)) bookmarks.delete(pageId);
      else bookmarks.add(pageId);
      writeBookmarks(bookmarks);
      render();
    });
    render();
  }

  const noteInput = document.getElementById('page-note');
  const noteStatus = document.getElementById('note-status');
  if (pageId && noteInput) {
    const notes = readNotes();
    noteInput.value = typeof notes[pageId] === 'string' ? notes[pageId] : '';
    let timer = null;
    noteInput.addEventListener('input', () => {
      window.clearTimeout(timer);
      if (noteStatus) noteStatus.textContent = 'Saving…';
      timer = window.setTimeout(() => {
        const nextNotes = readNotes();
        const value = noteInput.value.trim();
        if (value) nextNotes[pageId] = value;
        else delete nextNotes[pageId];
        writeNotes(nextNotes);
        if (noteStatus) noteStatus.textContent = value ? 'Saved in this browser.' : 'Note removed.';
      }, 250);
    });
  }

  const renderNextStep = (container, eyebrow = 'Continue learning') => {
    if (!container || !guidedPath.length) return;
    const completed = readProgress();
    const nextItem = guidedPath.find((item) => !completed.has(item.id));
    const completeCount = guidedPath.filter((item) => completed.has(item.id)).length;
    if (nextItem) {
      const itemKind = nextItem.kind === 'practice'
        ? 'Applied task'
        : nextItem.kind === 'assessment'
          ? 'Readiness check'
          : nextItem.kind === 'capstone'
            ? 'Capstone'
            : 'Lesson';
      container.innerHTML = `
        <p class="eyebrow">${escapeHtml(eyebrow)} · ${escapeHtml(itemKind)}</p>
        <h2><a href="${nextItem.url}">${escapeHtml(nextItem.title)}</a></h2>
        <p>${completeCount} of ${guidedPath.length} guided-path items complete.</p>`;
    } else {
      container.innerHTML = '<p class="eyebrow">Program complete</p><h2>All guided work is complete ✓</h2><p><a href="completion.html">Open your completion summary</a>, or use the reference library and workspace for future projects.</p>';
    }
  };

  renderNextStep(document.getElementById('continue-learning'));
  renderNextStep(document.getElementById('next-recommended-step'), 'Next recommended step');

  const completedForContinue = readProgress();
  const nextForContinue = guidedPath.find((item) => !completedForContinue.has(item.id));
  const courseRoot = document.querySelector('.brand')?.href || window.location.href;
  document.querySelectorAll('[data-continue-link]').forEach((link) => {
    if (nextForContinue) {
      link.href = new URL(nextForContinue.url, courseRoot).href;
      link.setAttribute('aria-label', `Continue Learning: ${nextForContinue.title}`);
    } else {
      link.href = new URL('completion.html', courseRoot).href;
      link.setAttribute('aria-label', 'Continue Learning: course completion summary');
    }
  });

  const dashboard = document.getElementById('progress-dashboard');
  if (dashboard && lessons.length) {
    const completed = readProgress();
    const lessonCount = lessons.filter((lesson) => completed.has(lesson.id)).length;
    const milestoneCount = milestones.filter((item) => completed.has(item.id)).length;
    const totalCount = lessons.length + milestones.length;
    const completeCount = lessonCount + milestoneCount;
    const percent = totalCount ? Math.round((completeCount / totalCount) * 100) : 0;
    const groups = new Map();
    lessons.forEach((lesson) => {
      if (!groups.has(lesson.module)) groups.set(lesson.module, []);
      groups.get(lesson.module).push(lesson);
    });
    const responseData = readResponses();
    const missedLessonChecks = Object.entries(responseData)
      .filter(([key, value]) => key.startsWith('lesson-check-') && value && value.correct === false)
      .map(([key]) => Number(key.replace('lesson-check-', '')))
      .map((number) => lessons.find((lesson) => Number(lesson.lesson) === number))
      .filter(Boolean);
    const openReadiness = Object.entries(responseData)
      .filter(([key, value]) => key.includes('readiness-check') && value && value.passed === false)
      .map(([key]) => milestones.find((item) => item.id === key))
      .filter(Boolean);
    const reviewItems = [
      ...missedLessonChecks.map((lesson) => `<li><a href="${lesson.url}">${escapeHtml(lesson.title)}</a> — revisit the lesson decision check</li>`),
      ...openReadiness.map((item) => `<li><a href="${item.url}">${escapeHtml(item.title)}</a> — review the explanations and linked lessons</li>`),
    ];
    const reviewHtml = reviewItems.length
      ? `<section class="progress-review"><h2>Review focus</h2><p>Open the exact item that needs another look:</p><ul>${reviewItems.join('')}</ul></section>`
      : '';
    const completionHtml = totalCount > 0 && completeCount === totalCount
      ? '<section class="course-complete"><h2>Course complete</h2><p>You have completed every lesson, applied task, readiness check, and the capstone.</p><p><a href="completion.html">Open the completion summary</a> to review or print a personal record.</p></section>'
      : '';
    const modulesHtml = [...groups.entries()].map(([module, moduleLessons]) => {
      const moduleComplete = moduleLessons.filter((lesson) => completed.has(lesson.id)).length;
      const task = milestones.find((item) => item.kind === 'practice' && item.module === module);
      const taskDone = task ? completed.has(task.id) : false;
      const assessment = milestones.find((item) => item.kind === 'assessment' && item.module === module);
      const assessmentDone = assessment ? completed.has(assessment.id) : false;
      const lessonHtml = moduleLessons.map((lesson) => {
        const done = completed.has(lesson.id);
        return `<li class="${done ? 'done' : ''}"><a href="${lesson.url}">${escapeHtml(lesson.title)}</a>${done ? ' <span aria-label="complete">✓</span>' : ''}</li>`;
      }).join('');
      const taskHtml = task
        ? `<li class="milestone ${taskDone ? 'done' : ''}"><a href="${task.url}">${escapeHtml(task.title)}</a>${taskDone ? ' <span aria-label="complete">✓</span>' : ''}</li>`
        : '';
      const assessmentHtml = assessment
        ? `<li class="milestone ${assessmentDone ? 'done' : ''}"><a href="${assessment.url}">${escapeHtml(assessment.title)}</a>${assessmentDone ? ' <span aria-label="complete">✓</span>' : ''}</li>`
        : '';
      return `<details><summary>Module ${module}: ${moduleComplete}/${moduleLessons.length} lessons${task ? `; task ${taskDone ? 'complete' : 'open'}` : ''}${assessment ? `; check ${assessmentDone ? 'passed' : 'open'}` : ''}</summary><ul>${lessonHtml}${taskHtml}${assessmentHtml}</ul></details>`;
    }).join('');
    const capstone = milestones.find((item) => item.kind === 'capstone');
    const capstoneDone = capstone ? completed.has(capstone.id) : false;
    const capstoneHtml = capstone
      ? `<div class="capstone-progress ${capstoneDone ? 'done' : ''}"><strong>Final capstone</strong><a href="${capstone.url}">${escapeHtml(capstone.title)}</a><span>${capstoneDone ? 'Complete ✓' : 'Not yet complete'}</span></div>`
      : '';
    dashboard.innerHTML = `${completionHtml}${reviewHtml}
      <div class="progress-summary"><strong>${completeCount} of ${totalCount} tracked items complete</strong><span>${percent}%</span></div>
      <div class="progress-bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${percent}" aria-label="${percent}% complete"><span style="width:${percent}%"></span></div>
      <p class="progress-breakdown">${lessonCount}/${lessons.length} lessons · ${milestoneCount}/${milestones.length} applied-learning milestones</p>
      <div class="module-progress">${modulesHtml}</div>
      ${capstoneHtml}`;
  }

  const completionSummary = document.querySelector('[data-completion-summary]');
  const printCompletion = document.getElementById('print-completion');
  if (completionSummary) {
    const completed = readProgress();
    const tasks = milestones.filter((item) => item.kind === 'practice');
    const checks = milestones.filter((item) => item.kind === 'assessment');
    const capstone = milestones.find((item) => item.kind === 'capstone');
    const lessonDone = lessons.filter((item) => completed.has(item.id)).length;
    const taskDone = tasks.filter((item) => completed.has(item.id)).length;
    const checkDone = checks.filter((item) => completed.has(item.id)).length;
    const capstoneDone = capstone ? completed.has(capstone.id) : false;
    const total = lessons.length + tasks.length + checks.length + (capstone ? 1 : 0);
    const complete = lessonDone + taskDone + checkDone + (capstoneDone ? 1 : 0);
    const finished = total > 0 && complete === total;
    if (finished) {
      const generatedDate = new Intl.DateTimeFormat('en-US', { dateStyle: 'long' }).format(new Date());
      completionSummary.innerHTML = `
        <section class="completion-record">
          <p class="eyebrow">Personal learning record</p>
          <h2>Practical AI Learning completed</h2>
          <p>You completed the full guided program, including the final capstone.</p>
          <dl class="completion-stats">
            <div><dt>Lessons</dt><dd>${lessonDone} of ${lessons.length}</dd></div>
            <div><dt>Applied tasks</dt><dd>${taskDone} of ${tasks.length}</dd></div>
            <div><dt>Readiness checks</dt><dd>${checkDone} of ${checks.length}</dd></div>
            <div><dt>Capstone</dt><dd>Complete</dd></div>
          </dl>
          <p class="completion-date">Summary generated ${escapeHtml(generatedDate)}.</p>
          <p class="muted">This is a personal self-study record, not an accredited certificate or professional credential.</p>
          <p><a href="start.html#initial-self-assessment">Repeat the opening self-assessment</a> and compare how your reasoning has changed.</p>
        </section>`;
      if (printCompletion) printCompletion.hidden = false;
    } else {
      const nextItem = guidedPath.find((item) => !completed.has(item.id));
      completionSummary.innerHTML = `
        <section class="completion-pending">
          <p class="eyebrow">Still in progress</p>
          <h2>${complete} of ${total} guided items complete</h2>
          <p>Finish the remaining lessons, applied tasks, readiness checks, and capstone before generating a completion summary.</p>
          ${nextItem ? `<p><a href="${nextItem.url}">Continue with ${escapeHtml(nextItem.title)} →</a></p>` : ''}
        </section>`;
    }
  }
  printCompletion?.addEventListener('click', () => window.print());

  const pageRecord = (id) => {
    const lesson = lessons.find((item) => item.id === id);
    if (lesson) return { ...lesson, kind: 'lesson' };
    const milestone = milestones.find((item) => item.id === id);
    if (milestone) return milestone;
    const searchable = searchIndex.find((item) => item.id === id);
    if (searchable) return searchable;
    return { id, title: id, url: '', kind: 'content' };
  };

  const workspace = document.getElementById('workspace-dashboard');
  if (workspace) {
    const bookmarks = readBookmarks();
    const notes = readNotes();
    const ids = [...new Set([...bookmarks, ...Object.keys(notes)])];
    const items = ids
      .map((id) => ({ ...pageRecord(id), id, note: typeof notes[id] === 'string' ? notes[id] : '', bookmarked: bookmarks.has(id) }))
      .sort((a, b) => String(a.title).localeCompare(String(b.title)));
    if (!items.length) {
      workspace.innerHTML = '<p>No saved pages yet. Use the bookmark button or notes field on a lesson, task, source packet, capstone, or reference page.</p>';
    } else {
      workspace.innerHTML = items.map((item) => {
        const title = item.url
          ? `<a href="${item.url}">${escapeHtml(item.title)}</a>`
          : escapeHtml(item.title);
        return `<article class="workspace-item"><p class="eyebrow">${escapeHtml(item.kind || 'content')}${item.bookmarked ? ' · Bookmarked' : ''}</p><h2>${title}</h2>${item.note ? `<p class="saved-note">${escapeHtml(item.note)}</p>` : '<p class="muted">No note saved.</p>'}</article>`;
      }).join('');
    }
  }

  const exportButton = document.getElementById('export-progress');
  if (exportButton) {
    exportButton.textContent = 'Export learning data';
    exportButton.addEventListener('click', () => {
      const completed = readProgress();
      const bookmarks = readBookmarks();
      const notes = readNotes();
      const responses = readResponses();
      const payload = {
        product: 'Practical AI Learning',
        format_version: 3,
        exported_at: new Date().toISOString(),
        completed_ids: [...completed],
        bookmark_ids: [...bookmarks],
        notes,
        activity_responses: responses,
        completed_lessons: lessons.filter((item) => completed.has(item.id)),
        completed_milestones: milestones.filter((item) => completed.has(item.id)),
      };
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'practical-ai-learning-data.json';
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    });
  }

  const importButton = document.getElementById('import-progress');
  const importFile = document.getElementById('import-progress-file');
  const progressStatus = document.getElementById('progress-status');
  if (importButton && importFile) {
    importButton.textContent = 'Import learning data';
    importButton.addEventListener('click', () => importFile.click());
    importFile.addEventListener('change', async () => {
      const file = importFile.files && importFile.files[0];
      if (!file) return;
      try {
        const payload = JSON.parse(await file.text());
        if (!payload || !Array.isArray(payload.completed_ids)) {
          throw new Error('The selected file is not a valid learning-data export.');
        }
        const contentIds = new Set(searchIndex.map((item) => item.id).filter(Boolean));
        const progressIds = new Set([
          ...lessons.map((item) => item.id),
          ...milestones.map((item) => item.id),
        ]);
        const allowed = new Set([...contentIds, ...progressIds]);
        const restored = [...new Set(payload.completed_ids)]
          .filter((id) => typeof id === 'string' && progressIds.has(id));
        const restoredBookmarks = Array.isArray(payload.bookmark_ids)
          ? [...new Set(payload.bookmark_ids)].filter((id) => typeof id === 'string' && allowed.has(id))
          : [];
        const restoredNotes = {};
        if (payload.notes && typeof payload.notes === 'object' && !Array.isArray(payload.notes)) {
          Object.entries(payload.notes).forEach(([id, value]) => {
            if (allowed.has(id) && typeof value === 'string' && value.trim()) {
              restoredNotes[id] = value.slice(0, 20000);
            }
          });
        }
        const restoredResponses = {};
        if (payload.activity_responses && typeof payload.activity_responses === 'object' && !Array.isArray(payload.activity_responses)) {
          const allowedResponseId = /^(module-\d{2}-(activity|readiness-check)|initial-self-assessment|lesson-check-[a-z0-9-]+|capstone-project)$/;
          Object.entries(payload.activity_responses).forEach(([activityId, values]) => {
            if (!allowedResponseId.test(activityId)) return;
            const cleanValues = sanitizeImportedValue(values);
            if (cleanValues && typeof cleanValues === 'object' && Object.keys(cleanValues).length) {
              restoredResponses[activityId] = cleanValues;
            }
          });
        }
        writeProgress(new Set(restored));
        writeBookmarks(new Set(restoredBookmarks));
        writeNotes(restoredNotes);
        writeResponses(restoredResponses);
        if (progressStatus) {
          progressStatus.textContent = `Imported ${restored.length} completed item${restored.length === 1 ? '' : 's'}, ${restoredBookmarks.length} bookmark${restoredBookmarks.length === 1 ? '' : 's'}, ${Object.keys(restoredNotes).length} note${Object.keys(restoredNotes).length === 1 ? '' : 's'}, and ${Object.keys(restoredResponses).length} worksheet${Object.keys(restoredResponses).length === 1 ? '' : 's'}. Reloading…`;
        }
        window.setTimeout(() => window.location.reload(), 500);
      } catch (error) {
        if (progressStatus) {
          progressStatus.textContent = error instanceof Error
            ? error.message
            : 'The learning-data file could not be imported.';
        }
      } finally {
        importFile.value = '';
      }
    });
  }

  const resetButton = document.getElementById('reset-progress');
  if (resetButton) {
    resetButton.addEventListener('click', () => {
      if (!window.confirm('Reset all lesson, task, readiness-check, and capstone progress in this browser? Saved notes and bookmarks will remain.')) return;
      localStorage.removeItem(progressKey);
      window.location.reload();
    });
  }

  const clearWorkspace = document.getElementById('clear-workspace');
  const workspaceStatus = document.getElementById('workspace-status');
  if (clearWorkspace) {
    clearWorkspace.addEventListener('click', () => {
      if (!window.confirm('Clear all bookmarks and notes in this browser? Course progress will remain.')) return;
      localStorage.removeItem(bookmarksKey);
      localStorage.removeItem(notesKey);
      if (workspaceStatus) workspaceStatus.textContent = 'Bookmarks and notes cleared. Reloading…';
      window.setTimeout(() => window.location.reload(), 350);
    });
  }

  const searchInput = document.getElementById('site-search');
  const searchResults = document.getElementById('search-results');
  if (searchInput && searchResults) {
    const renderSearch = () => {
      const query = searchInput.value.trim().toLowerCase();
      if (query.length < 2) {
        searchResults.innerHTML = '<p class="muted">Enter at least two characters.</p>';
        return;
      }
      const terms = query.split(/\s+/).filter(Boolean);
      const results = searchIndex
        .map((item) => {
          const haystack = `${item.title} ${item.summary} ${item.kind}`.toLowerCase();
          const score = terms.reduce((total, term) => total + (haystack.includes(term) ? 1 : 0), 0);
          return { item, score };
        })
        .filter((result) => result.score === terms.length)
        .slice(0, 30);
      searchResults.innerHTML = results.length
        ? results.map(({ item }) => `<article class="search-result"><p class="eyebrow">${escapeHtml(item.kind)}</p><h2><a href="${item.url}">${escapeHtml(item.title)}</a></h2><p>${escapeHtml(item.summary)}</p></article>`).join('')
        : '<p>No matching pages found. Try fewer or broader terms.</p>';
    };
    searchInput.addEventListener('input', renderSearch);
    renderSearch();
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, (char) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
    }[char]));
  }
})();
