import { useCreateSurveyProvider } from "./CreateSurveyProvider";
import React, { useEffect, useState } from "react";
import { PlusIcon2 } from "./Icons";
import QuestionList from "./QuestionList";
import { motion } from "framer-motion";

const CreateSurvey = ({ initialSurvey }) => { // accept generated survey
  const {
    questions,
    defaultQuestionType,
    setSurveyTitle,
    setSurveyDescription,
    setQuestions,              //use existing setter instead of replaceQuestions
    surveyTitle,
    surveyDescription,
    addNewQuestion,
  } = useCreateSurveyProvider();

  const [titleLength, setTitleLength] = useState(0);
  const [descriptionLength, setDescriptionLength] = useState(0);
  const [titleError, setTitleError] = useState("");
  const [descriptionError, setDescriptionError] = useState("");

  //  when a generated survey arrives, populate title/desc/questions
  useEffect(() => {
    if (!initialSurvey) return;

    // 1) title / description (backend doesn’t send description)
    setSurveyTitle(initialSurvey.title || "");
    setSurveyDescription("");

    // 2) normalize API questions → app shape
    const now = Date.now();
    const toOptionObj = (text, j) => ({ id: now + Math.random() + j, text: String(text ?? "") });

    const normalized = (initialSurvey.questions || []).map((q, i) => {
      const base = { id: now + i + Math.random(), title: q?.text || "", saved: false };

      switch (q?.type) {
        case "multiple_choice":
          return {
            ...base,
            type: "multipleChoice",
            options: (q.options || []).map(toOptionObj),
          };

        case "rating": {
          const scale = Math.max(2, Math.min(Number(q.scale) || 5, 10));
          const opts = Array.from({ length: scale }, (_, k) => toOptionObj(String(k + 1), k));
          return {
            ...base,
            type: "singleChoice",   // renderable with your existing single-choice UI
            options: opts,
          };
        }

        case "open_text":
        default:
          return {
            ...base,
            type: "shortAnswer",
            options: [],
          };
      }
    });

    setQuestions(normalized); //single atomic replace
  }, [initialSurvey, setSurveyTitle, setSurveyDescription, setQuestions]);

  useEffect(() => {
    setTitleLength(surveyTitle?.length || 0);
    setDescriptionLength(surveyDescription?.length || 0);
  }, [surveyTitle, surveyDescription]);

  return (
    <div className="flex h-full font-switzer lg:overflow-auto scrollbar-style flex-col gap-4 sm:gap-6 sm:p-4">
      <div className="flex flex-col space-y-6">
        {/* Title Input */}
        <motion.div
          whileHover={{ boxShadow: "0 4px 12px rgba(0, 0, 0, 0.05)" }}
          className="rounded-[12px] shadow-sm w-full border border-[#00000020] bg-white flex flex-col transition-all duration-300"
        >
          <motion.input
            type="text"
            maxLength={500}
            name="title"
            value={surveyTitle}
            onChange={(e) => {
              const value = e.target.value;
              setSurveyTitle(value);
              setTitleLength(value.length);
              setTitleError(value.length >= 500 ? "Title cannot exceed 500 characters." : "");
            }}
            placeholder="Enter survey title"
            className="text-[16px] px-5 pt-4 pb-1 text-primary outline-none border-none bg-transparent rounded-t-[12px] transition-all duration-200"
          />
          <div className="px-5 pb-3 text-right">
            <p className={`text-[10px] ${titleLength > 450 ? "text-amber-500" : "text-gray-400"}`}>
              {titleLength}/500
            </p>
            {titleError && <p className="text-red-500 text-sm">{titleError}</p>}
          </div>
        </motion.div>

        {/* Description Input */}
        <motion.div
          whileHover={{ boxShadow: "0 4px 12px rgba(0, 0, 0, 0.05)" }}
          className="rounded-[12px] shadow-sm w-full border border-[#00000020] bg-white flex flex-col transition-all duration-300"
        >
          <motion.input
            type="text"
            placeholder="Enter survey description"
            maxLength={100}
            name="description"
            value={surveyDescription}
            onChange={(e) => {
              const value = e.target.value;
              setSurveyDescription(value);
              setDescriptionLength(value.length);
              setDescriptionError(value.length >= 100 ? "Description cannot exceed 100 characters." : "");
            }}
            className="text-[16px] px-5 pt-4 pb-1 text-primary outline-none border-none bg-transparent rounded-t-[12px] transition-all duration-200"
          />
          <div className="px-5 pb-3 text-right">
            <p className={`text-[10px] ${descriptionLength > 90 ? "text-amber-500" : "text-gray-400"}`}>
              {descriptionLength}/100
            </p>
            {descriptionError && (
              <p className="text-red-500 text-xs">{descriptionError}</p>
            )}
          </div>
        </motion.div>
      </div>

      {/* Question List */}
      <div className="flex-1">
        <QuestionList questions={questions} />
      </div>

      {/* Add Question Button */}
      <motion.div
        whileHover={{ scale: 1.01, borderColor: '#6851a7 ' }}
        className="border-2 py-4 md:py-5 lg:py-6 rounded-[12px] flex justify-center border-dotted border-[#6851a7] bg-[#6851a7]/5 transition-all duration-300"
      >
        <motion.button
          whileHover={{ scale: 1.05, boxShadow: "0 6px 20px rgba(108, 93, 211, 0.3)" }}
          whileTap={{ scale: 0.95 }}
          onClick={() => addNewQuestion(defaultQuestionType)}
          className="bg-[#6851a7] flex gap-2 items-center text-white py-3 px-6 rounded-full shadow-sm transition-all duration-300"
        >
          <PlusIcon2 className="h-4 w-4" />
          <span className="font-medium text-base">Add Question</span>
        </motion.button>
      </motion.div>
    </div>
  );
};

export default CreateSurvey;