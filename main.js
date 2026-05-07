document.addEventListener("DOMContentLoaded", (event) => {

    // ----------------------------------------------------
    // 0. 手機版漢堡選單開關邏輯 (Mobile Menu)
    // ----------------------------------------------------
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.getElementById('navLinks');

    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener('click', () => {
            // 切換按鈕的 X 動畫狀態與選單的展開狀態
            mobileMenuBtn.classList.toggle('active');
            navLinks.classList.toggle('active');
        });

        // 點擊選單內的連結後，自動收起選單 (提升 UX)
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                mobileMenuBtn.classList.remove('active');
                navLinks.classList.remove('active');
            });
        });
    }

    // 檢查 GSAP 是否有成功載入
    if (typeof gsap !== 'undefined') {
        // 註冊 GSAP ScrollTrigger 插件
        gsap.registerPlugin(ScrollTrigger);

        // ----------------------------------------------------
        // 1. 載入進場爆發力動效 (Hero Section)
        // ----------------------------------------------------
        // 確保目前頁面有 Hero 區塊才執行 (避免在子頁面報錯)
        if (document.querySelector(".hero-subtitle")) {
            const heroTl = gsap.timeline();

            heroTl.from(".hero-subtitle", {
                y: 30,
                opacity: 0,
                duration: 0.8,
                ease: "power3.out",
                delay: 0.2
            })
            .from(".hero-title", {
                y: 50,
                opacity: 0,
                duration: 1,
                ease: "back.out(1.5)" // 彈性爆發感
            }, "-=0.4")
            .from(".hero-desc", {
                y: 20,
                opacity: 0,
                duration: 0.8,
                ease: "power2.out"
            }, "-=0.6")
            .from(".hero .btn", {
                scale: 0.8,
                opacity: 0,
                duration: 0.5,
                ease: "back.out(2)"
            }, "-=0.4");
        }

        // ----------------------------------------------------
        // 2. 滾動揭示動效 (Scroll Reveal)
        // ----------------------------------------------------
        const revealElements = document.querySelectorAll(".gs-reveal");

        revealElements.forEach((elem) => {
            gsap.fromTo(elem,
                { autoAlpha: 0, y: 50 },
                {
                    duration: 1,
                    autoAlpha: 1,
                    y: 0,
                    ease: "power3.out",
                    scrollTrigger: {
                        trigger: elem,
                        start: "top 85%", // 當元素頂部到達視窗 85% 高度時觸發
                        toggleActions: "play none none reverse" // 往下滾動播放，往上滾動還原
                    }
                }
            );
        });
    }

    // ----------------------------------------------------
    // 3. Navbar 滾動陰影變化
    // ----------------------------------------------------
    const navbar = document.getElementById("navbar");
    if (navbar) {
        window.addEventListener("scroll", () => {
            if (window.scrollY > 50) {
                navbar.style.boxShadow = "0 4px 20px rgba(0,0,0,0.1)";
            } else {
                navbar.style.boxShadow = "0 2px 15px rgba(0,0,0,0.05)";
            }
        });
    }
});