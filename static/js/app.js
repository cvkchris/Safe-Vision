document.addEventListener("DOMContentLoaded", function () {
    const video = document.getElementById("video-feed");
    const spinner = document.getElementById("loading-spinner");

    // Show spinner until the video is ready to play
    video.addEventListener("waiting", () => {
        spinner.style.display = "block";
    });
    video.addEventListener("playing", () => {
        spinner.style.display = "none";
    });
});
