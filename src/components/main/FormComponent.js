import React, { useState } from 'react';
import { useForm } from 'react-hook-form';

const FormComponent = () => {
    const [organizerSignatureType, setOrganizerSignatureType] = useState('text');
    const [hodInputType, setHodInputType] = useState('text');
    const [speakerProfileType, setSpeakerProfileType] = useState('text'); // 'text' or 'image'
    const [actionTakenReportType, setActionTakenReportType] = useState('text');
    const [uploadedFiles, setUploadedFiles] = useState({});
    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
        setValue
    } = useForm();

    async function formSubmitHandler(data) {
        // console.log(data["reportPrepared"])
        console.log(data);
        let formData = new FormData();

        // Clean up signature data based on input type
        const cleanedData = {
            header: data.header,
            generalInfo: data.generalInfo,
            speaker: data.speaker,
            participants: data.participants,
            synopsis: data.synopsis,
            reportPrepared: {
                ...data.reportPrepared,
                // Only include organizer text if text input is selected
                ...(organizerSignatureType === 'text' && { signature: data.reportPrepared?.signature }),
            },
            signatures: {
                // Only include HOD text if text input is selected
                ...(hodInputType === 'text' && { hodText: data.signatures?.hodText }),
                // Only include HOD file if image input is selected
                // ...(hodInputType === 'image' && { hod: data.signatures?.hod })
            },
            speakerProfile: {
                ...(speakerProfileType === 'text' && { text: data.speakerProfileText }),
            },
            actionTakenReport: {
                ...(actionTakenReportType === 'text' && { text: data.actionTakenReportText }),
            }
        };

        formData.append('data', JSON.stringify(cleanedData));
        const appendFiles = (fieldName, files) => {
            if (!files) {
                console.warn(`No files found for ${fieldName}`);
                return;
            }

            try {
                Array.from(files).forEach((file, index) => {
                    formData.append(`${fieldName}_${index}`, file);
                });
            } catch (error) {
                console.error(`Error appending files for ${fieldName}:`, error);
            }
        };

        if (speakerProfileType === 'image' && data.annexure?.speaker_profile) {
            const { speaker_profile } = data.annexure
            if (speaker_profile) {
                appendFiles('speaker_profile', data.annexure.speaker_profile);
            }
        }

        if (hodInputType === 'image' && data?.signatures?.hod) {
            appendFiles('hod_signature', data.signatures.hod);
        }
        if (organizerSignatureType === 'image' && data?.reportPreparedBy?.signature) {
            appendFiles('organizer_signature', data.reportPreparedBy.signature);
        }

        if (actionTakenReportType === 'image' && data?.annexure?.action_taken_report) {
            appendFiles('action_taken_report', data.annexure.action_taken_report);
        }
        Object.entries(data.annexure).forEach(([section, files]) => {
            const isConditionalSection =
                section === 'speaker_profile' ||
                section === 'action_taken_report';

            if (!isConditionalSection) {
                appendFiles(section, files);
            }
        });

        // Log FormData contents
        for (const [key, value] of formData.entries()) {
            console.log(key, "\n", value, "\n");
        }
        try {
            const response = await fetch('https://report-generator-college-project.onrender.com/generate-pdf', {
            // const response = await fetch('http://localhost:3001/generate-pdf', {
                method: 'POST',
                body: formData
            });
            formData = {}
            if (response) {
                // Handle PDF download
                console.log("Response from backend : ", response)
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'event_report.pdf';
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
                        {[
                            { name: 'name', label: 'Name of the Organiser *' },
                            { name: 'designation', label: 'Designation/Title *' },
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
                        <div className="flex flex-col">
                            <label>Signature *</label>
                            <div className="flex space-x-4">
                                <label>
                                    <input
                                        type="radio"
                                        value="text"
                                        checked={organizerSignatureType === 'text'}
                                        onChange={() => {
                                            setOrganizerSignatureType('text');
                                            setValue('reportPreparedBy.signature', undefined);
                                            setUploadedFiles(prev => ({ ...prev, organizer_signature: null }));
                                        }}
                                    /> Text
                                </label>
                                <label>
                                    <input
                                        type="radio"
                                        value="image"
                                        checked={organizerSignatureType === 'image'}
                                        onChange={() => {
                                            setOrganizerSignatureType('image');
                                            setValue('reportPrepared.signature', '');
                                        }}
                                    /> Image
                                </label>
                            </div>
                            {organizerSignatureType === 'text' ? (
                                <input
                                    {...register('reportPrepared.signature', {
                                        required: organizerSignatureType === 'text' ? 'This field is required' : false
                                    })}
                                    className="border p-2 rounded"
                                />
                            ) : (
                                <div className="relative border-2 border-dashed border-gray-300 rounded-lg p-4 hover:border-[#4472c4] transition-colors">
                                    <input
                                        type="file"
                                        accept="image/*"
                                        {...register('reportPreparedBy.signature', {
                                            required: organizerSignatureType === 'image' ? 'Signature is required' : false,
                                            onChange: (e) => handleFileChange('organizer_signature', e.target.files)
                                        })}
                                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                    />
                                    <div className="text-center">
                                        {uploadedFiles.organizer_signature ? (
                                            <div className="space-y-1">
                                                <span className="text-[#4472c4] font-medium">Uploaded:</span>
                                                {uploadedFiles.organizer_signature.map((name, i) => (
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
                            )}
                            {organizerSignatureType === 'text' && errors.reportPrepared?.signature && (
                                <span className="text-red-500 text-sm">
                                    {errors.reportPrepared.signature.message}
                                </span>
                            )}
                            {organizerSignatureType === 'image' && errors.reportPreparedBy?.signature && (
                                <span className="text-red-500 text-sm">
                                    {errors.reportPreparedBy.signature.message}
                                </span>
                            )}
                        </div>
                    </div>
                </fieldset>
                {/* Signatures Section */}
                <fieldset className="bg-white shadow-sm rounded-lg p-6 hover:shadow-md transition-shadow">
                    <legend className="text-xl font-bold text-gray-900 bg-[#4472c4] text-white px-4 py-2 rounded-full">
                        Signatures
                    </legend>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                        <div className="flex flex-col space-y-2">
                            <label className="font-medium text-gray-700">HOD Signature *</label>
                            <div className="flex space-x-4">
                                <label>
                                    <input
                                        type="radio"
                                        value="text"
                                        checked={hodInputType === 'text'}
                                        // onChange={() => setHodInputType('text')}
                                        onChange={() => {
                                            setHodInputType('text');
                                            // Reset image input when switching to text
                                            setValue('signatures.hod', undefined);
                                            setUploadedFiles(prev => ({ ...prev, hod_signature: null }));
                                        }}
                                    /> Text
                                </label>
                                <label>
                                    <input
                                        type="radio"
                                        value="image"
                                        checked={hodInputType === 'image'}
                                        onChange={() => { setHodInputType('image'); setValue('signatures.hodText', ''); }

                                        }
                                    /> Image
                                </label>
                            </div>

                            {hodInputType === 'text' ? (
                                <input
                                    {...register('signatures.hodText', {
                                        required: hodInputType === 'text' ? 'HOD Signature is required' : false
                                    })}
                                    className="border p-2 rounded"
                                />
                            ) : (
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
                            )}
                            {/* Error messages */}
                            {hodInputType === 'text' && errors.signatures?.hodText && (
                                <span className="text-red-600 text-sm italic">{errors.signatures.hodText.message}</span>
                            )}
                            {hodInputType === 'image' && errors.signatures?.hod && (
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
                            if (section === 'Speaker Profile') {
                                return (
                                    <div key="speaker_profile" className="flex flex-col space-y-2">
                                        <label className="font-medium text-gray-700">Speaker Profile *</label>
                                        <div className="flex space-x-4">
                                            <label>
                                                <input
                                                    type="radio"
                                                    value="text"
                                                    checked={speakerProfileType === 'text'}
                                                    onChange={() => {
                                                        setSpeakerProfileType('text');
                                                        setValue('annexure.speaker_profile', undefined); // Clear files
                                                        setUploadedFiles(prev => ({ ...prev, speaker_profile: null }));
                                                    }}
                                                /> Text
                                            </label>
                                            <label>
                                                <input
                                                    type="radio"
                                                    value="image"
                                                    checked={speakerProfileType === 'image'}
                                                    onChange={() => {
                                                        setSpeakerProfileType('image');
                                                        setValue('speakerProfileText', ''); // Clear text input
                                                    }}
                                                /> Image
                                            </label>
                                        </div>

                                        {speakerProfileType === 'text' ? (
                                            <textarea
                                                {...register('speakerProfileText')}
                                                className="border p-2 rounded"
                                                rows={4}
                                                placeholder="Enter speaker profile details..."
                                            />
                                        ) : (
                                            <div className="relative border-2 border-dashed border-gray-300 rounded-lg p-4 hover:border-[#4472c4] transition-colors">
                                                <input
                                                    type="file"
                                                    multiple
                                                    // {...register('annexure.speaker_profile'), {
                                                    //     onChange: (e) => handleFileChange('speaker_profile', e.target.files)
                                                    // }}
                                                    {...register(`annexure.speaker_profile`, {
                                                        required: `${section} is required`,
                                                        onChange: (e) => handleFileChange('speaker_profile', e.target.files)
                                                    })}
                                                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                                />
                                                <div className="text-center">
                                                    {uploadedFiles.speaker_profile ? (
                                                        <div className="space-y-1">
                                                            <span className="text-[#4472c4] font-medium">Uploaded Image:</span>
                                                            {uploadedFiles.speaker_profile.map((name, i) => (
                                                                <p key={i} className="text-sm text-gray-700 truncate">
                                                                    {name}
                                                                </p>
                                                            ))}
                                                        </div>
                                                    ) : (
                                                        <>
                                                            <span className="text-[#4472c4] font-medium">Click to upload speaker's image (Only one)</span>
                                                            <p className="text-sm text-gray-500">PNG, JPG up to 2MB</p>
                                                        </>
                                                    )}
                                                </div>
                                            </div>
                                        )}

                                        {/* {speakerProfileType === 'text' && errors.speakerProfileText && (
                                            <span className="text-red-600 text-sm italic">{errors.speakerProfileText.message}</span>
                                        )}
                                        {speakerProfileType === 'image' && errors.annexure?.speaker_profile && (
                                            <span className="text-red-600 text-sm italic">{errors.annexure.speaker_profile.message}</span>
                                        )} */}
                                    </div>
                                )
                            }
                            if (section === 'Action Taken Report') {

                                return (
                                    <div>
                                        {/* Action Taken Report Section */}
                                        <div key="action_taken_report" className="flex flex-col space-y-2">
                                            <label className="font-medium text-gray-700">Action Taken Report *</label>
                                            <div className="flex space-x-4">
                                                <label>
                                                    <input
                                                        type="radio"
                                                        value="text"
                                                        checked={actionTakenReportType === 'text'}
                                                        onChange={() => {
                                                            setActionTakenReportType('text');
                                                            setValue('annexure.action_taken_report', undefined);
                                                            setUploadedFiles(prev => ({ ...prev, action_taken_report: null }));
                                                        }}
                                                    /> Text
                                                </label>
                                                <label>
                                                    <input
                                                        type="radio"
                                                        value="image"
                                                        checked={actionTakenReportType === 'image'}
                                                        onChange={() => {
                                                            setActionTakenReportType('image');
                                                            setValue('actionTakenReportText', '');
                                                        }}
                                                    /> Image
                                                </label>
                                            </div>

                                            {actionTakenReportType === 'text' ? (
                                                <textarea
                                                    {...register('actionTakenReportText', {
                                                        required: actionTakenReportType === 'text' ? 'Action Taken Report is required' : false,
                                                    })}
                                                    className="border p-2 rounded"
                                                    rows={4}
                                                    placeholder="Enter action taken report details..."
                                                />
                                            ) : (
                                                <div className="relative border-2 border-dashed border-gray-300 rounded-lg p-4 hover:border-[#4472c4] transition-colors">
                                                    <input
                                                        type="file"
                                                        multiple
                                                        {...register('annexure.action_taken_report', {
                                                            required: actionTakenReportType === 'image' ? 'Action Taken Report is required' : false,
                                                            onChange: (e) => handleFileChange('action_taken_report', e.target.files)
                                                        })}
                                                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                                    />
                                                    <div className="text-center">
                                                        {uploadedFiles.action_taken_report ? (
                                                            <div className="space-y-1">
                                                                <span className="text-[#4472c4] font-medium">Uploaded Images:</span>
                                                                {uploadedFiles.action_taken_report.map((name, i) => (
                                                                    <p key={i} className="text-sm text-gray-700 truncate">
                                                                        {name}
                                                                    </p>
                                                                ))}
                                                            </div>
                                                        ) : (
                                                            <>
                                                                <span className="text-[#4472c4] font-medium">Click to upload images</span>
                                                                <p className="text-sm text-gray-500">Multiple images allowed - PNG, JPG up to 2MB</p>
                                                            </>
                                                        )}
                                                    </div>
                                                </div>
                                            )}

                                            {actionTakenReportType === 'text' && errors.actionTakenReportText && (
                                                <span className="text-red-600 text-sm italic">{errors.actionTakenReportText.message}</span>
                                            )}
                                            {actionTakenReportType === 'image' && errors.annexure?.action_taken_report && (
                                                <span className="text-red-600 text-sm italic">{errors.annexure.action_taken_report.message}</span>
                                            )}
                                        </div>
                                    </div>

                                )
                            }
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
                                                    <span className="text-[#4472c4] font-medium">Uploaded Images:</span>
                                                    {uploadedFiles[fieldName].map((name, i) => (
                                                        <p key={i} className="text-sm text-gray-700 truncate">
                                                            {name}
                                                        </p>
                                                    ))}
                                                </div>
                                            ) : (
                                                <>
                                                    <span className="text-[#4472c4] font-medium">Click to upload Images</span>
                                                    <p className="text-sm text-gray-500">Multiple images allowed - PNG, JPG up to 2MB</p>
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
