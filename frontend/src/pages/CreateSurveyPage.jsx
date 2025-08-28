import { useState } from "react";
import DashboardLayout from "../component/DashboardLayout";
import CreateSurvey from "../component/CreateSurvey";
import CreateSurveySidebar from "../component/CreateSurveySidebar";
import Header from "../component/Header";
import GenerateSurveyButton from "../component/GenerateSurveryButton";

const CreateSurveyPage = ({ surveySeriesId = "defaultId" }) => {
  const [generatedSurvey, setGeneratedSurvey] = useState(null);

  return (
    <DashboardLayout>
      <div className="flex flex-col w-full h-full overflow-hidden">
        <div className="lg:min-h-[90px]">
          <Header>
            <h2 className="text-[26px] font-switzerMedium text-primary">
              Create a New Survey
            </h2>
              <GenerateSurveyButton onLoaded={setGeneratedSurvey} />
          </Header>
        </div>
        <div className="flex grow w-full overflow-hidden h-full">
          <div className="grow p-3 sm:p-2 w-full overflow-auto h-[calc(100vh-164px)] sm:h-[calc(100vh-192px)] md:h-[calc(100vh-192px)] lg:h-[calc(100vh-148px)] xl:h-full scrollbar-style">
            <div className="block lg:hidden">
              <CreateSurveySidebar surveySeriesId={surveySeriesId} />
            </div>
            <CreateSurvey />
          </div>
          <div className="hidden lg:block min-w-[280px] p-3 max-w-[280px] overflow-auto scrollbar-style h-[calc(100vh-89px)]">
            <CreateSurveySidebar surveySeriesId={surveySeriesId} />
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default CreateSurveyPage;
