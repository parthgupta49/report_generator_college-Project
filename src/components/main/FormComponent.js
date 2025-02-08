import React, { useState } from 'react';
import { useForm } from 'react-hook-form';

const FormComponent = () => {
    // ... existing useForm and formSubmitHandler code remains the same ...
    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm();

    async function formSubmitHandler(data) {
        console.log(data)
        const formData = new FormData();

        // Append JSON data
        formData.append('data', JSON.stringify({
            header: data.header,
            generalInfo: data.generalInfo,
            speaker: data.speaker,
            participants: data.participants,
            synopsis: data.synopsis,
            reportPrepared: data.reportPrepared
        }));


        // Append files
        const appendFiles = (fieldName, files) => {
            Array.from(files).forEach((file, index) => {
                formData.append(`${fieldName}_${index}`, file);
            });
        };

        // Signatures
        appendFiles('hod_signature', data.signatures.hod);

        // Annexure files
        Object.entries(data.annexure).forEach(([section, files]) => {
            appendFiles(section, files);
        });

        // Log FormData contents
        for (const [key, value] of formData.entries()) {
            console.log(key, value);
        }
        try {
            const response = await fetch('http://localhost:3001/generate-pdf', {
                method: 'POST',
                body: formData
            });

            if (response) {
                // Handle PDF download
                console.log("Response from backend : ", response)
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'report.pdf';
                document.body.appendChild(a);
                a.click();
                a.remove();
            }
            else {
                console.log('No response from the backend | Error generating PDF');
            }

        } catch (error) {
            console.error('Error:', error);
        }

    }

    const [uploadedFiles, setUploadedFiles] = useState({});

    const handleFileChange = (fieldName, files) => {
        setUploadedFiles(prev => ({
            ...prev,
            [fieldName]: Array.from(files).map(file => file.name)
        }));
    };

    return (
        <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
            <form onSubmit={handleSubmit(formSubmitHandler)} className="max-w-6xl mx-auto space-y-6">
                {/* Header Section */}
                <fieldset className="bg-white shadow-sm rounded-lg p-6 hover:shadow-md transition-shadow">
                    <legend className="text-xl font-bold text-gray-900 bg-[#4472c4] text-white px-4 py-2 rounded-full">
                        Header Information
                    </legend>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                        {/* ... header input fields remain the same ... */}
                        <div className="flex flex-col">
                            <label>Activity Name *</label>
                            <input
                                {...register('header.activityName', { required: 'Activity Name is required' })}
                                className="border p-2 rounded"
                            />
                            {errors.header?.activityName && (
                                <span className="text-red-500 text-sm">{errors.header.activityName.message}</span>
                            )}
                        </div>

                        <div className="flex flex-col">
                            <label>Activity Date *</label>
                            <input
                                type="text"
                                {...register('header.activityDate', { required: 'Activity Date is required' })}
                                className="border p-2 rounded"
                            />
                            {errors.header?.activityDate && (
                                <span className="text-red-500 text-sm">{errors.header.activityDate.message}</span>
                            )}
                        </div>
                    </div>
                </fieldset>

                {/* General Information Section */}
                <fieldset className="bg-white shadow-sm rounded-lg p-6 hover:shadow-md transition-shadow">
                    <legend className="text-xl font-bold text-gray-900 bg-[#4472c4] text-white px-4 py-2 rounded-full">
                        General Information
                    </legend>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                        {/* ... general info inputs remain the same ... */}
                        {[
                            { name: 'type', label: 'Type of Activity *' },
                            { name: 'title', label: 'Title of Activity *' },
                            { name: 'time', label: 'Time *' },
                            { name: 'venue', label: 'Venue *' },
                            { name: 'collaboration', label: 'Collaboration/Sponsor' },
                            { name: 'sdgs', label: 'SDGs Linked *' },
                            { name: 'website', label: 'Website/Platform Link' },
                            { name: 'videos', label: 'Video Links' },
                        ].map((field) => (
                            <div key={field.name} className="flex flex-col">
                                <label>{field.label}</label>
                                <input
                                    {...register(`generalInfo.${field.name}`, {
                                        required: field.label.includes('*') ? 'This field is required' : false
                                    })}
                                    className="border p-2 rounded"
                                />
                                {errors.generalInfo?.[field.name] && (
                                    <span className="text-red-500 text-sm">
                                        {errors.generalInfo[field.name].message}
                                    </span>
                                )}
                            </div>
                        ))}
                    </div>
                </fieldset>

                {/* Speaker Details Section */}
                <fieldset className="bg-white shadow-sm rounded-lg p-6 hover:shadow-md transition-shadow">
                    <legend className="text-xl font-bold text-gray-900 bg-[#4472c4] text-white px-4 py-2 rounded-full">
                        Speaker Details
                    </legend>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                        {/* ... speaker inputs remain the same ... */}
                        {[
                            { name: 'name', label: 'Name *' },
                            { name: 'title', label: 'Title/Position *' },
                            { name: 'organization', label: 'Organization *' },
                            { name: 'presentation', label: 'Presentation Title *' },
                        ].map((field) => (
                            <div key={field.name} className="flex flex-col">
                                <label>{field.label}</label>
                                <input
                                    {...register(`speaker.${field.name}`, { required: 'This field is required' })}
                                    className="border p-2 rounded"
                                />
                                {errors.speaker?.[field.name] && (
                                    <span className="text-red-500 text-sm">
                                        {errors.speaker[field.name].message}
                                    </span>
                                )}
                            </div>
                        ))}
                    </div>
                </fieldset>

                {/* Participants Section */}
                <fieldset className="bg-white shadow-sm rounded-lg p-6 hover:shadow-md transition-shadow">
                    <legend className="text-xl font-bold text-gray-900 bg-[#4472c4] text-white px-4 py-2 rounded-full">
                        Participants Profile
                    </legend>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                        {/* ... participant inputs remain the same ... */}
                        {[
                            { name: 'type', label: 'Type of Participants *' },
                            { name: 'total', label: 'Total Participants *' },
                            { name: 'christStudents', label: 'CHRIST Students *' },
                            { name: 'christFaculty', label: 'CHRIST Faculty *' },
                            { name: 'otherStudents', label: 'Other Students *' },
                            { name: 'otherFaculty', label: 'Other Faculty / Participants *' },
                        ].map((field) => (
                            <div key={field.name} className="flex flex-col">
                                <label>{field.label}</label>
                                <input
                                    {...register(`participants.${field.name}`, { required: 'This field is required' })}
                                    className="border p-2 rounded"
                                />
                                {errors.participants?.[field.name] && (
                                    <span className="text-red-500 text-sm">
                                        {errors.participants[field.name].message}
                                    </span>
                                )}
                            </div>
                        ))}
                    </div>
                </fieldset>

                {/* Synopsis Section */}
                <fieldset className="bg-white shadow-sm rounded-lg p-6 hover:shadow-md transition-shadow">
                    <legend className="text-xl font-bold text-gray-900 bg-[#4472c4] text-white px-4 py-2 rounded-full">
                        Synopsis (Description)
                    </legend>
                    <div className="grid grid-cols-1 gap-6 mt-4">
                        {/* ... synopsis textareas remain the same ... */}
                        {[
                            { name: 'highlights', label: 'Highlights *', type: 'textarea' },
                            { name: 'takeaways', label: 'Key Takeaways *', type: 'textarea' },
                            { name: 'summary', label: 'Summary *', type: 'textarea' },
                            { name: 'followup', label: 'Follow-up Plan *', type: 'textarea' },
                        ].map((field) => (
                            <div key={field.name} className="flex flex-col">
                                <label>{field.label}</label>
                                <textarea rows="2"
                                    {...register(`synopsis.${field.name}`, { required: 'This field is required' })}
                                    className="border p-2 rounded h-32"
                                />
                                {errors.synopsis?.[field.name] && (
                                    <span className="text-red-500 text-sm">
                                        {errors.synopsis[field.name].message}
                                    </span>
                                )}
                            </div>
                        ))}
                    </div>
                </fieldset>

                {/* Report Prepared Section */}
                <fieldset className="bg-white shadow-sm rounded-lg p-6 hover:shadow-md transition-shadow">
                    <legend className="text-xl font-bold text-gray-900 bg-[#4472c4] text-white px-4 py-2 rounded-full">
                        Report Prepared By
                    </legend>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                        {/* ... report prepared inputs remain the same ... */}
                        {[
                            { name: 'name', label: 'Name of the Organiser *' },
                            { name: 'designation', label: 'Designation/Title *' },
                            { name: 'Signature', label: 'Signature *' },
                        ].map((field) => (
                            <div key={field.name} className="flex flex-col">
                                <label>{field.label}</label>
                                <input
                                    {...register(`reportPrepared.${field.name}`, { required: 'This field is required' })}
                                    className="border p-2 rounded"
                                />
                                {errors.reportPrepared?.[field.name] && (
                                    <span className="text-red-500 text-sm">
                                        {errors.reportPrepared[field.name].message}
                                    </span>
                                )}
                            </div>
                        ))}
                    </div>
                </fieldset>

                {/* Signatures Section */}
                {/* <fieldset className="bg-white shadow-sm rounded-lg p-6 hover:shadow-md transition-shadow">
                    <legend className="text-xl font-bold text-gray-900 bg-[#4472c4] text-white px-4 py-2 rounded-full">
                        Signatures
                    </legend>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                        <div className="flex flex-col space-y-2">
                            <label className="font-medium text-gray-700">HOD Signature *</label>
                            <div className="relative border-2 border-dashed border-gray-300 rounded-lg p-4 hover:border-[#4472c4] transition-colors">
                                <input
                                    type="file"
                                    accept="image/*"
                                    {...register('signatures.hod', { required: 'HOD Signature is required' })}
                                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                />
                                <div className="text-center">
                                    <span className="text-[#4472c4] font-medium">Click to upload signature</span>
                                    <p className="text-sm text-gray-500">PNG, JPG up to 2MB</p>
                                </div>
                            </div>
                            {errors.signatures?.hod && (
                                <span className="text-red-600 text-sm italic">{errors.signatures.hod.message}</span>
                            )}
                        </div>
                    </div>
                </fieldset> */}

                {/* Annexure Section */}
                {/* <fieldset className="bg-white shadow-sm rounded-lg p-6 hover:shadow-md transition-shadow">
                    <legend className="text-xl font-bold text-gray-900 bg-[#4472c4] text-white px-4 py-2 rounded-full">
                        Annexure
                    </legend>
                    <div className="grid grid-cols-1 gap-6 mt-4">
                        {[
                            'Speaker Profile',
                            'Activity Photos',
                            'Attendance',
                            'Brochure/Poster',
                            'Website Screenshots',
                            'Student Feedback',
                            'Action Taken Report'
                        ].map((section) => (
                            <div key={section} className="flex flex-col space-y-2">
                                <label className="font-medium text-gray-700">{section} *</label>
                                <div className="relative border-2 border-dashed border-gray-300 rounded-lg p-4 hover:border-[#4472c4] transition-colors">
                                    <input
                                        type="file"
                                        multiple
                                        {...register(`annexure.${section.toLowerCase().replace(/ /g, '_')}`, {
                                            required: `${section} is required`
                                        })}
                                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                    />
                                    <div className="text-center">
                                        <span className="text-[#4472c4] font-medium">Click to upload files</span>
                                        <p className="text-sm text-gray-500">Multiple files allowed</p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </fieldset> */}

                {/* Signatures Section */}
                <fieldset className="bg-white shadow-sm rounded-lg p-6 hover:shadow-md transition-shadow">
                    <legend className="text-xl font-bold text-gray-900 bg-[#4472c4] text-white px-4 py-2 rounded-full">
                        Signatures
                    </legend>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                        <div className="flex flex-col space-y-2">
                            <label className="font-medium text-gray-700">HOD Signature *</label>
                            <div className="relative border-2 border-dashed border-gray-300 rounded-lg p-4 hover:border-[#4472c4] transition-colors">
                                <input
                                    type="file"
                                    accept="image/*"
                                    {...register('signatures.hod', {
                                        required: 'HOD Signature is required',
                                        onChange: (e) => handleFileChange('hod_signature', e.target.files)
                                    })}
                                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                />
                                <div className="text-center">
                                    {uploadedFiles.hod_signature ? (
                                        <div className="space-y-1">
                                            <span className="text-[#4472c4] font-medium">Uploaded:</span>
                                            {uploadedFiles.hod_signature.map((name, i) => (
                                                <p key={i} className="text-sm text-gray-700 truncate">
                                                    {name}
                                                </p>
                                            ))}
                                        </div>
                                    ) : (
                                        <>
                                            <span className="text-[#4472c4] font-medium">Click to upload signature</span>
                                            <p className="text-sm text-gray-500">PNG, JPG up to 2MB</p>
                                        </>
                                    )}
                                </div>
                            </div>
                            {errors.signatures?.hod && (
                                <span className="text-red-600 text-sm italic">{errors.signatures.hod.message}</span>
                            )}
                        </div>
                    </div>
                </fieldset>

                {/* Annexure Section */}
                <fieldset className="bg-white shadow-sm rounded-lg p-6 hover:shadow-md transition-shadow">
                    <legend className="text-xl font-bold text-gray-900 bg-[#4472c4] text-white px-4 py-2 rounded-full">
                        Annexure
                    </legend>
                    <div className="grid grid-cols-1 gap-6 mt-4">
                        {[
                            'Speaker Profile',
                            'Activity Photos',
                            'Attendance',
                            'Brochure/Poster',
                            'Website Screenshots',
                            'Student Feedback',
                            'Action Taken Report'
                        ].map((section) => {
                            const fieldName = section.toLowerCase().replace(/ /g, '_');
                            return (
                                <div key={section} className="flex flex-col space-y-2">
                                    <label className="font-medium text-gray-700">{section} *</label>
                                    <div className="relative border-2 border-dashed border-gray-300 rounded-lg p-4 hover:border-[#4472c4] transition-colors">
                                        <input
                                            type="file"
                                            multiple
                                            {...register(`annexure.${fieldName}`, {
                                                required: `${section} is required`,
                                                onChange: (e) => handleFileChange(fieldName, e.target.files)
                                            })}
                                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                        />
                                        <div className="text-center">
                                            {uploadedFiles[fieldName] ? (
                                                <div className="space-y-1">
                                                    <span className="text-[#4472c4] font-medium">Uploaded Files:</span>
                                                    {uploadedFiles[fieldName].map((name, i) => (
                                                        <p key={i} className="text-sm text-gray-700 truncate">
                                                            {name}
                                                        </p>
                                                    ))}
                                                </div>
                                            ) : (
                                                <>
                                                    <span className="text-[#4472c4] font-medium">Click to upload files</span>
                                                    <p className="text-sm text-gray-500">Multiple files allowed</p>
                                                </>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </fieldset>

                <button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full bg-[#4472c4] text-white py-3 px-6 rounded-lg font-medium hover:bg-[#365a9d] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {isSubmitting ? 'Generating Report...' : 'Generate Report'}
                </button>
            </form>
        </div>
    );
};

export default FormComponent;