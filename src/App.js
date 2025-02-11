import FormComponent from './components/main/FormComponent';
function App() {
  return (
    <div className="w-screen h-screen overflow-x-hidden">
      <div className='flex lg:flex-row flex-col  justify-center pt-2 gap-10 items-center'>
        <img src='https://christuniversity.in/images/logo.jpg' alt='Christ-logo' className=' lg:w-[16rem]' />
        <div className='border-1 self-stretch hidden lg:block'></div>
        <div className='text-xl font-medium'> <p className='text-center lg:text-justify'>Department Of Computer Science</p><p className='text-center'>BYC</p></div>
      </div>
      <div className='text-center text-lg mt-5'> Activity Report Generator</div>

      <FormComponent />
      <div className='py-8 bg-[#002147] text-white font-medium'>
        <div className='flex justify-center lg:flex-row flex-col gap-[1rem] lg:gap-[4rem] items-center lg:items-stretch'>
          <div className='flex flex-col'>
            {/* <img src='https://christuniversity.in/uploads/campus/medium/1453155785_2023-08-17_12-25-20.jpg' className='max-w-[16rem] ' /> */}
            <img src='https://christuniversity.in/uploads/userfiles/ypr(2).jpg' alt='Christ-YPR logo' className='max-w-[16rem]  bg-center rounded-xl' />
            <span className='text-[25px]'>
              CHRIST <span className='text-[14px] font-normal'>(Deemed to be University)</span>
            </span>

            <span className='text-[15px] font-normal opacity-70 text-center lg:text-justify'>  Bangalore Yeshwanthpur Campus</span>
          </div>
          <div className='max-w-[50%] lg:max-w-[30%] flex flex-col lg:gap-8 lg:pt-0 gap-10 justify-center'>
            <div>
              <p className='text-[16px] text-center lg:text-justify'>VISION</p>
              <p className='text-[14px] text-center lg:text-justify font-normal'>&nbsp; EXCELLENCE AND SERVICE</p>
            </div>

            <div>
              <p className='text-[16px] text-center lg:text-justify'>MISSION</p>
              <p className='text-[14px] text-center lg:text-justify font-normal'>&nbsp; CHRIST (Deemed to be University) is a nurturing ground for an individual's holistic development to make effective contribution to the society in a dynamic environment.
              </p>
            </div>

          </div>
          <span className='lg:pt-9 flex flex-col text-center lg:text-justify'>
            <span className='opacity-70'>Website Developed by</span> <span className='underline cursor-pointer text-[#f5f505] text-[1.3rem]'><a href="https://github.com/parthgupta49/" target='_blank' rel='noreferrer' >Parth Gupta | BCA(2022) </a></span>
          </span>
        </div>
      </div>
    </div>
  );
}

export default App;
