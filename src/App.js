import FormComponent from './components/main/FormComponent';
function App() {
  return (
    <div className="w-screen h-screen overflow-x-hidden">
          <div className='flex justify-center items-center text-xl py-3 bg-[#ad3489] text-white font-medium'>
              Developed with <span className='text-[#f71625] text-3xl'>&nbsp;&hearts;&nbsp;</span> By&nbsp;<span className='underline cursor-pointer text-[#f5f505] text-[1.3rem]'><a href="https://github.com/parthgupta49/" target='_blank'>Parth Gupta</a></span>
          </div>
          <FormComponent/>
    </div>
  );
}

export default App;
