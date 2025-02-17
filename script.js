// ฟังก์ชันที่ใช้เปลี่ยนเนื้อหาภายในหน้าเมื่อคลิกที่ลิงก์ใน sidebar
function loadContent(contentType) {
    var mainContent = document.getElementById('main-content');
    var slideshow = document.getElementById('slideshow'); // เข้าถึง slideshow
    var certishow = document.getElementById('certishow');
    var contactshow = document.getElementById('contactshow');
    var titleshow = document.getElementById('title-content');
    var Mypicture = document.getElementById('Mypicture');
    var history = document.getElementById('history');
    if (contentType === 'Main Page') {
        mainContent.innerHTML = `
        <h3>Nanawin Sukksam</h3>
        <h5>IoT Systems Engineering & Industrial Physics Student</h5>
        <p>
            Hello, I'm Nanawin Sukksam, a passionate student at King Mongkut's Institute of Technology Ladkrabang, 
            where I am pursuing a double degree in IoT Systems Engineering and Industrial Physics. My academic journey 
            has equipped me with a unique blend of skills in both cutting-edge technology and applied physics, driving my 
            curiosity and problem-solving abilities.
        </p>
        <p>
            I am particularly passionate about web development and aspire to become a professional in the field. 
            I find joy in transforming complex problems into elegant, user-friendly digital solutions. With a solid 
            foundation in IoT systems, I aim to integrate my expertise in web development to create impactful and innovative 
            web experiences.
        </p>
        <p class="motto">
            "Nothing is too difficult if we keep learning."
        </p>
        <a href="https://www.youtube.com/channel/UCVt6X-sbnDUG2iiovywb5lA" class="btn">My Video</a>
        `;
        slideshow.style.display = 'block'; // แสดง slideshow
        certishow.style.display = 'none';
        contactshow.style.display = 'flex';
        titleshow.style.display = 'flex';
        Mypicture.style.display = 'none';
        history.style.display = 'none';
        
    } else if (contentType === 'Personal history') {
        mainContent.innerHTML = `
            <h1>Personal history</h1>
            <p></p>
        `;
        stopSlides(); // หยุดสไลด์โชว์
        slideshow.style.display = 'none'; // ซ่อน slideshow
        certishow.style.display = 'none';
        contactshow.style.display = 'none';
        titleshow.style.display = 'none';
        Mypicture.style.display = 'block';
        history.style.display = 'block';

    } else if (contentType === 'performance') {
        mainContent.innerHTML = `
            <h1>Portfolio</h1>
            <p>This is another personal portfolio. Add your details, projects, or any other information here.</p>
        `;
        slideshow.style.display = 'none'; // ซ่อน slideshow
        certishow.style.display = 'none';
        contactshow.style.display = 'none';
        titleshow.style.display = 'none';
        Mypicture.style.display = 'none';
        history.style.display = 'none';
    }
      else if (contentType === 'certificate') {
        mainContent.innerHTML = `
            <h1>Certificate</h1>
        `;
        certishow.style.display = 'flex' //
        slideshow.style.display = 'none'; // ซ่อน slideshow
        contactshow.style.display = 'none';
        titleshow.style.display = 'none';
        Mypicture.style.display = 'none';
        history.style.display = 'none';
    }
}

let slideIndex = 0;
let slideInterval; // ประกาศตัวแปร slideInterval
let slideTrack = document.querySelector(".slideshow-track");

// ฟังก์ชันเริ่มสไลด์โชว์
function showSlides() {
    let slides = document.getElementsByClassName("slideshow");

    // ซ่อนภาพทั้งหมดก่อน
    for (let i = 0; i < slides.length; i++) {
        slides[i].classList.remove("active");
        
    }

    // เพิ่มค่า index ของสไลด์
    slideIndex++;

    // ถ้าเกินจำนวนสไลด์ที่มี ก็กลับไปอันแรก
    if (slideIndex > slides.length) {
        slideIndex = 1;
    }

    // แสดงภาพปัจจุบัน
    slides[slideIndex - 1].classList.add("active");

    // ตั้งเวลาเลื่อนสไลด์ทุก 5 วินาที (5000 มิลลิวินาที)
    slideInterval = setTimeout(showSlides,5000); // ปรับตรงนี้เพื่อเลื่อนช้าลง
}

// ฟังก์ชันหยุดสไลด์โชว์
function stopSlides() {
    clearTimeout(slideInterval); // หยุดการเปลี่ยนภาพอัตโนมัติ
    let slides = document.getElementsByClassName("slideshow");
    for (let i = 0; i < slides.length; i++) {
        slides[i].classList.remove("active");
    }
}

// ตรวจสอบ URL ของหน้าเว็บและทำงานตามนั้น
function initializeSlideshow() {
    let slideshow = document.getElementById("slideshow");

    // ตรวจสอบ URL ของหน้าเว็บ
    if (window.location.pathname === 'Main Page' || window.location.pathname === 'Main Page') {
        // ถ้าเป็นหน้า main page ให้เริ่มสไลด์โชว์
        slideshow.style.display = 'block'; // แสดงสไลด์โชว์
        showSlides();
    } else {
        // ถ้าไม่ใช่หน้า main page ให้หยุดสไลด์โชว์
        stopSlides();
        slideshow.style.display = 'none'; // ซ่อนสไลด์โชว์
    }
}

// หยุดสไลด์โชว์ทันทีเมื่อเปลี่ยนหน้า
window.addEventListener('beforeunload', function () {
    stopSlides();
});

// เรียกฟังก์ชันเมื่อโหลดหน้า
initializeSlideshow();

document.addEventListener('DOMContentLoaded', function () {
    var sidebar = document.getElementById('sidebar');
    var settingsButton = document.getElementById('settings-button');

    // ตรวจสอบสถานะของ sidebar
    function checkSidebar() {
        if (sidebar.style.left = `${-180}px`) {
            settingsButton.style.visibility = 'hidden'; // ซ่อนปุ่มเมื่อ sidebar ถูกซ่อน
        } else {
            settingsButton.style.visibility = 'visible'; // แสดงปุ่มเมื่อ sidebar ปรากฏ
        }
    }

      // ฟังการเลื่อนของ sidebar
      sidebar.addEventListener('transitionend', checkSidebar);

      // ตรวจสอบสถานะเริ่มต้น
      checkSidebar();


});