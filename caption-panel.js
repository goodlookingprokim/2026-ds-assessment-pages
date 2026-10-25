/* Keep instructional screens clear while preserving native captions in fullscreen. */
document.querySelectorAll('video').forEach((video) => {
  const trackElement = video.querySelector('track[kind="captions"], track[kind="subtitles"]');
  if (!trackElement) return;

  const panel = document.createElement('div');
  panel.className = 'caption-panel';
  panel.setAttribute('role', 'region');
  panel.setAttribute('aria-label', '영상 자막');
  const label = document.createElement('span');
  label.className = 'caption-panel-label';
  label.textContent = '자막';
  const line = document.createElement('span');
  line.textContent = '자막을 불러오는 중…';
  panel.append(label, line);
  video.classList.add('caption-panel-video');
  video.insertAdjacentElement('afterend', panel);

  const track = trackElement.track;
  track.mode = 'hidden';

  function render() {
    if (track.mode !== 'hidden') return;
    const active = Array.from(track.activeCues || []);
    const cues = active.length ? active : Array.from(track.cues || []).filter((cue) =>
      cue.startTime <= video.currentTime && video.currentTime < cue.endTime);
    line.textContent = cues.map((cue) => cue.text).join('\n');
  }

  function syncFullscreen() {
    const fullscreen = document.fullscreenElement === video ||
      document.webkitFullscreenElement === video || video.webkitDisplayingFullscreen;
    track.mode = fullscreen ? 'showing' : 'hidden';
    panel.hidden = Boolean(fullscreen);
    if (!fullscreen) render();
  }

  track.addEventListener('cuechange', render);
  trackElement.addEventListener('load', render);
  trackElement.addEventListener('error', () => {
    line.textContent = '자막을 불러오지 못했습니다. 영상 자막 설정을 확인하세요.';
  });
  video.addEventListener('timeupdate', render);
  video.addEventListener('seeked', render);
  video.addEventListener('webkitbeginfullscreen', syncFullscreen);
  video.addEventListener('webkitendfullscreen', syncFullscreen);
  document.addEventListener('fullscreenchange', syncFullscreen);
  document.addEventListener('webkitfullscreenchange', syncFullscreen);
  render();
});
